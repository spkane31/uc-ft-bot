import json
import math
import os
import time
from datetime import datetime

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd
from requests_oauthlib import OAuth1Session
import requests

load_dotenv()

ROUNDING_PRECISION = 1
SEASON_YEAR = 2026  # Current season year


def get_oauth_token() -> tuple[str, str]:
    if (
        os.getenv("TWITTER_OAUTH_TOKEN") is not None
        and os.getenv("TWITTER_OAUTH_TOKEN_SECRET") is not None
    ):
        print("Using existing OAuth tokens")
        return os.getenv("TWITTER_OAUTH_TOKEN"), os.getenv("TWITTER_OAUTH_TOKEN_SECRET")

    print("No OAuth tokens found, generating new ones")

    consumer_key = os.environ.get("TWITTER_API_KEY")
    consumer_secret = os.environ.get("TWITTER_API_SECRET")

    # Get request token
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )
        raise

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print(f"Got OAuth token: {resource_owner_key}")
    print(f"Got OAuth token secret: {resource_owner_secret}")

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print(f"Please go here and authorize: {authorization_url}")
    verifier = input("Paste the PIN here: ")

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    print(f"Got OAuth token: {access_token}")
    print(f"Got OAuth token secret: {access_token_secret}")
    return access_token, access_token_secret


def consecutive_make_percentage(made: int, attempted: int, goal_pct: float) -> int:
    return math.ceil((goal_pct * attempted - made) / (1 - goal_pct))


def missed_opportunities(made: int, attempted: int, goal_pct: float = 0.75) -> int:
    # How many extra free throws would the team have made had they shot goal_pct
    return min(0, math.ceil((made - goal_pct * attempted) / goal_pct))


def get_free_throw_attempts() -> tuple[int, int]:
    # URL of the page
    url = f"https://www.sports-reference.com/cbb/schools/cincinnati/men/{SEASON_YEAR}.html"

    # Fetch the HTML content
    response = requests.get(url)

    # Ensure the request was successful
    if response.status_code == 200:
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the specific table using its id
        table = soup.find("table", id="season-total_totals")

        if table:
            # Extract table rows
            rows = table.find_all("tr")

            table = []

            # Parse the table data
            data = []
            for row in rows:
                # Extract all cells (both header and data)

                cells = row.find_all(["th", "td"])
                # Extract the text from each cell

                cell_values = [cell.text.strip() for cell in cells]

                data.append(cell_values)

            # Convert the data into a pandas DataFrame
            data[0][0] = "Player"
            df = pd.DataFrame(data[1:], columns=data[0])

            # Print the DataFrame
            print(df)

            # Free Throw Attempts are in the FT and FTA columns with "Team" as the first column entry
            ft = df.loc[df["Player"] == "Team", "FT"].values[0]
            fta = df.loc[df["Player"] == "Team", "FTA"].values[0]

            print(f"Free Throws Made: {ft}")
            print(f"Free Throw Attempts: {fta}")

            return int(ft), int(fta)

        else:
            raise ValueError("Failed to locate the table")
    else:
        raise ValueError(f"Failed to fetch page: {response.status_code}")


def get_schedule() -> pd.DataFrame:
    # Schedule uses the year the season starts (SEASON_YEAR)
    url = f"https://www.sports-reference.com/cbb/schools/cincinnati/men/{SEASON_YEAR}-schedule.html"

    # Fetch the HTML content
    response = requests.get(url)

    # Ensure the request was successful
    if response.status_code == 200:
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the specific table using its id
        table = soup.find("table", id="schedule")

        if table:
            # Extract table rows
            rows = table.find_all("tr")

            table = []

            # Parse the table data
            data = []
            for row in rows:
                # Extract all cells (both header and data)

                cells = row.find_all(["th", "td"])
                # Extract the text from each cell

                cell_values = [
                    cell.text.strip() + ";" + cell.find("a")["href"]
                    if cell.find("a")
                    else cell.text.strip()
                    for cell in cells
                ]

                data.append(cell_values)

            # Convert the data into a pandas DataFrame
            df = pd.DataFrame(data[1:], columns=data[0])

            return df

        else:
            raise ValueError("Failed to locate the table")
    else:
        raise ValueError(f"Failed to fetch page: {response.status_code}")


def get_game_free_throws(url: str) -> tuple[int, int]:
    # Fetch the HTML content
    response = requests.get("https://www.sports-reference.com" + url)

    # Ensure the request was successful
    if response.status_code == 200:
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate the specific table using its id
        table = soup.find("table", id="box-score-basic-cincinnati")

        if table:
            # Extract table rows
            rows = table.find_all("tr")

            table = []

            # Parse the table data
            data = []
            for row in rows:
                # Extract all cells (both header and data)

                cells = row.find_all(["th", "td"])
                # Extract the text from each cell

                cell_values = [
                    cell.text.strip() + ";" + cell.find("a")["href"]
                    if cell.find("a")
                    else cell.text.strip()
                    for cell in cells
                ]

                data.append(cell_values)

            data[1][0] = "Player"
            # Convert the data into a pandas DataFrame
            df = pd.DataFrame(data[2:], columns=data[1])

            print(df)

            # Free Throw Attempts are in the FT and FTA columns, the Team one has the Player column as "School Totals"
            ft = df.loc[df["Player"] == "School Totals", "FT"].values[0]
            fta = df.loc[df["Player"] == "School Totals", "FTA"].values[0]

            return int(ft), int(fta)

        else:
            raise ValueError("Failed to locate the table")
    else:
        raise ValueError(f"Failed to fetch page: {response.status_code}")


def send_telegram_notification(message: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = 7333806927
    # bot = Bot(token=bot_token)

    # bot.send_message(chat_id=chat_id, text=message)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Define the payload for the request
    payload = {"chat_id": chat_id, "text": message}

    # Send the message using a POST request
    response = requests.post(url, data=payload)

    # Print the response (optional)
    print(response.json())


def read_season_data(year: int = SEASON_YEAR) -> tuple[int, int] | None:
    """Read the current season FT data from CSV. Returns (ftm, fta) or None if file doesn't exist."""
    file_path = f"data/season_stats_{year}.csv"
    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path)
        if len(df) == 0:
            return None
        # Get the most recent row
        last_row = df.iloc[-1]
        return int(last_row["ftm"]), int(last_row["fta"])
    except Exception as e:
        print(f"Error reading season data: {e}")
        return None


def write_season_data(ftm: int, fta: int, year: int = SEASON_YEAR) -> None:
    """Write the current season FT data to CSV."""
    file_path = f"data/season_stats_{year}.csv"
    data = {"timestamp": [datetime.now().isoformat()], "ftm": [ftm], "fta": [fta]}
    df = pd.DataFrame(data)

    # Append to file if it exists, otherwise create new
    if os.path.exists(file_path):
        df.to_csv(file_path, mode="a", header=False, index=False)
    else:
        df.to_csv(file_path, mode="w", header=True, index=False)

    print(f"Wrote season data to {file_path}: {ftm}/{fta}")


def has_data_changed(
    old_data: tuple[int, int] | None, new_data: tuple[int, int]
) -> bool:
    """Check if the season data has changed."""
    if old_data is None:
        print("No previous data found, treating as changed")
        return True

    old_ftm, old_fta = old_data
    new_ftm, new_fta = new_data

    if old_ftm != new_ftm or old_fta != new_fta:
        print(f"Data changed: {old_ftm}/{old_fta} -> {new_ftm}/{new_fta}")
        return True
    else:
        print(f"Data unchanged: {old_ftm}/{old_fta}")
        return False


if __name__ == "__main__":
    # Read old data before fetching new data
    old_data = read_season_data()
    print(f"Previous season data: {old_data}")

    # Fetch new season data
    ftm, fta = get_free_throw_attempts()
    new_data = (ftm, fta)
    print(f"Current season data: {new_data}")

    # Check if data has changed
    if not has_data_changed(old_data, new_data):
        print("No changes detected.")
        exit(0)

    # Data has changed, write to CSV
    write_season_data(ftm, fta)

    # Continue with Twitter posting logic
    consumer_key = os.environ.get("TWITTER_API_KEY")
    consumer_secret = os.environ.get("TWITTER_API_SECRET")

    access_token, access_token_secret = get_oauth_token()

    if None in [consumer_key, consumer_secret, access_token, access_token_secret]:
        if consumer_key is None:
            print("Missing Twitter API Key")
        if consumer_secret is None:
            print("Missing Twitter API Secret")
        if access_token is None:
            print("Missing Twitter Access Token")
        if access_token_secret is None:
            print("Missing Twitter Access Token Secret")
        raise ValueError("Missing Twitter API credentials")

    consecutive_makes = consecutive_make_percentage(ftm, fta, 0.75)

    print(f"Consecutive makes needed: {consecutive_makes}")

    schedule_df = get_schedule()

    print(schedule_df)

    # Get the last completed game
    last_game = schedule_df[
        (schedule_df["Tm"] != "") & (schedule_df["Opp"] != "")
    ].tail(1)

    # Keep only the desired columns
    last_game = last_game[["Date", "Time", "Opponent", "Tm", "Opp"]]

    game_date_href = last_game["Date"].iloc[0]
    game_opp_href = last_game["Opponent"].iloc[0]

    game_opp = game_opp_href.split(";")[0]

    print(f"Game Opponent: {game_opp}")

    game_date = game_date_href.split(";")[0]
    game_date_url = game_date_href.split(";")[1]

    game_ftm, game_fta = get_game_free_throws(game_date_url)

    print(f"Game Free Throws Made: {game_ftm}")
    print(f"Game Free Throw Attempts: {game_fta}")

    mo = missed_opportunities(game_ftm, game_fta)

    print(f"Missed Opportunities: {mo}")

    pt_differential = int(last_game["Tm"].iloc[0]) - int(last_game["Opp"].iloc[0])

    # Print the last game
    print("Last Completed Game:")
    print(last_game)

    # Format the date - handle format "Thu, Apr 3, 2025" to "Apr 3"
    try:
        # Try parsing format like "Thu, Apr 3, 2025"
        date_obj = datetime.strptime(game_date, "%a, %b %d, %Y")
    except ValueError:
        # Try parsing format like "2025-04-03"
        date_obj = datetime.strptime(game_date, "%Y-%m-%d")

    formatted_date = date_obj.strftime("%b %-d")

    # Add slightly celebratory but satirical tone if they shot over 75%
    game_pct = game_ftm / game_fta
    if game_pct > 0.75:
        msg = f"UC shot {game_ftm}/{game_fta} ({round(game_pct * 100, ROUNDING_PRECISION)}%) from the charity stripe vs {game_opp} on {formatted_date}, great job guys! But the Bearcats are still {ftm}/{fta} ({round(ftm / fta * 100, ROUNDING_PRECISION)}%) on the season and need {consecutive_makes} consecutive makes to reach 75%."
    else:
        msg = f"UC shot {game_ftm}/{game_fta} ({round(game_pct * 100, ROUNDING_PRECISION)}%) from the charity stripe vs {game_opp} on {formatted_date}. The Bearcats are now {ftm}/{fta} ({round(ftm / fta * 100, ROUNDING_PRECISION)}%) on the season and need {consecutive_makes} consecutive makes to reach 75%."

    # Would the missed_opportunity free throws have won the game?
    if mo > 0:
        if mo > pt_differential:
            msg += f" Had UC shot 75% from FT, they would have won by {mo - pt_differential} points."
        else:
            msg += f" Had UC shot 75% from FT, they would have lost by {pt_differential - mo} points."

    print(msg)

    print(f"Message length: {len(msg)}")

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    # Get the most recent tweet
    YOUR_TWITTER_USERNAME = "UC_FreeThrowBot"
    response = oauth.get(
        f"https://api.twitter.com/2/users/by/username/{YOUR_TWITTER_USERNAME}",
        params={"user.fields": "id"},
    )
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    user_id = response.json()["data"]["id"]
    print(f"User ID: {user_id}")

    response = oauth.get(
        f"https://api.twitter.com/2/users/{user_id}/tweets",
        params={
            "tweet.fields": "created_at",
            "max_results": 5,  # Has to be between 5 and 100
        },
    )
    if response.status_code != 200:
        if response.status_code == 429:
            print("Rate limit exceeded")
            reset_unix_time = int(response.headers["x-rate-limit-reset"])
            time_difference = reset_unix_time - int(time.time())
            minutes = time_difference // 60
            seconds = time_difference % 60
            print(
                f"Rate limit reset at {reset_unix_time}, please wait {minutes} minutes {seconds} seconds"
            )

        raise Exception(
            "Request returned an error: {} {} {}".format(
                response.status_code, response.text, response.headers
            )
        )
    recent_tweet = response.json()["data"][0]["text"]

    # Check if the most recent tweet is the same as the new tweet
    if recent_tweet == msg:
        print("Same content already tweeted")
    else:
        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json={"text": msg},
        )
        if response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        print("Response code: {}".format(response.status_code))
        # Saving the response as JSON
        json_response = response.json()
        print(json.dumps(json_response, indent=4, sort_keys=True))
        send_telegram_notification(f"Tweeted: {msg}, {json.dumps(json_response)}")
