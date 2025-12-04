# Setup Guide for UC Free Throw Bot

## GitHub Actions Secrets

To enable the automated daily tweets, you need to configure the following secrets in your GitHub repository:

### How to Add Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each of the following secrets:

### Required Secrets

| Secret Name | Description | Where to Find |
|------------|-------------|---------------|
| `TWITTER_API_KEY` | Twitter API consumer key | From Twitter Developer Portal |
| `TWITTER_API_SECRET` | Twitter API consumer secret | From Twitter Developer Portal |
| `TWITTER_OAUTH_TOKEN` | Twitter OAuth access token | Generated via OAuth flow |
| `TWITTER_OAUTH_TOKEN_SECRET` | Twitter OAuth access token secret | Generated via OAuth flow |

### Getting Twitter Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create or select your App
3. Navigate to "Keys and tokens"
4. Generate/copy:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret

## Workflow Schedule

The GitHub Action runs:
- **Daily at noon EST** (17:00 UTC)
- Can also be triggered manually from the Actions tab

## How It Works

1. **Fetch Data**: Script scrapes current season stats from sports-reference.com
2. **Check Changes**: Compares with previous data in `data/season_stats_2026.csv`
3. **Tweet**: If data changed, posts tweet and updates CSV
4. **Commit**: Creates a PR with the updated CSV
5. **Auto-merge**: PR is automatically merged to keep data in sync

## Manual Testing

To test the workflow manually:

1. Go to **Actions** tab in GitHub
2. Select "Daily Free Throw Tweet"
3. Click **Run workflow**
4. Select branch and run

## Local Development

To run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with credentials
cp .env.example .env
# Edit .env with your credentials

# Run script
python main.py
```

## Troubleshooting

### Workflow not running
- Check that the repository has Actions enabled
- Verify all secrets are properly configured
- Check the Actions tab for error logs

### PRs not auto-merging
- Ensure the workflow has `contents: write` and `pull-requests: write` permissions
- Check repository settings → Actions → General → Workflow permissions
- Enable "Allow GitHub Actions to create and approve pull requests"

### Duplicate tweets
- The script checks both:
  1. Season stats CSV for data changes
  2. Most recent tweet content to avoid duplicates
- If you see duplicates, check that CSV file is being properly committed
