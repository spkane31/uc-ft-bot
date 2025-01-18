import json
import math
import os

from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session
import requests
from bs4 import BeautifulSoup
import pandas as pd

load_dotenv()

ROUNDING_PRECISION = 1


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
    url = "https://www.sports-reference.com/cbb/schools/cincinnati/men/2025.html"

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
    url = (
        "https://www.sports-reference.com/cbb/schools/cincinnati/men/2025-schedule.html"
    )

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

        # # Find all tables and print out the id
        # tables = soup.find_all("table")
        # for table in tables:
        #     print(table.get("id"))

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

                print(cell_values)

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
    return -1, -1


if __name__ == "__main__":
    consumer_key = os.environ.get("TWITTER_API_KEY")
    consumer_secret = os.environ.get("TWITTER_API_SECRET")

    access_token, access_token_secret = get_oauth_token()

    ftm, fta = get_free_throw_attempts()

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

    msg = f"UC shot {game_ftm}/{game_fta} ({round(game_ftm / game_fta * 100, ROUNDING_PRECISION)}%) against {game_opp} on {game_date}, UC has shot {ftm}/{fta} on free throws ({round(ftm / fta * 100, ROUNDING_PRECISION)}%) this season. They need to make {consecutive_makes} consecutive free throws to reach 75% for the season."

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
