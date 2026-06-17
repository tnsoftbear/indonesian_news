# Scrap Bot

This application scrapes news from [Business Standard](https://www.business-standard.com/), translates articles into Hindi using OpenAI GPT, and publishes them to a Telegram channel.

## Features

- **Web Scraping** — Fetches latest news articles from Business Standard, including titles, content, and images.
- **AI Translation** — Translates articles to Hindi using OpenAI GPT-3.5-turbo.
- **Image Generation** — Optionally generates illustrations via DALL-E 2.
- **Telegram Publishing** — Sends formatted posts with images to your Telegram channel.
- **Deduplication** — Tracks sent articles to avoid duplicates across runs.

## Prerequisites

- **Docker** — [Install Docker Desktop](https://docs.docker.com/get-docker/)
- **Make** — Pre-installed on macOS/Linux. On macOS: `xcode-select --install`. On Linux: `sudo apt-get install build-essential`.

## Configuration

### 1. Create `.env` file

Copy the sample configuration file:

```sh
cp scrap/.env-sample scrap/.env
```

Then fill in the required variables in `scrap/.env`:

| Variable | Description | How to obtain |
|----------|-------------|---------------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | See [Creating a Telegram Bot](#creating-a-telegram-bot) below |
| `TELEGRAM_CHAT_ID` | Your channel ID or username | See [Finding Your Chat ID](#finding-your-chat-id) below |
| `OPENAI_API_KEY` | Your OpenAI API key | See [Getting an OpenAI API Key](#getting-an-openai-api-key) below |
| `SID` | Session cookie from Business Standard | See [Getting the SID Cookie](#getting-the-sid-cookie) below |

### 2. Obtaining Credentials

#### Creating a Telegram Bot

1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts to name your bot.
3. After creation, BotFather will give you a token like `6186948996:AAESaHBK8TGiu8PyXD1CI354EQ3IdLyH9rs`.
4. Copy this token and paste it as `TELEGRAM_BOT_TOKEN` in your `.env` file.
5. **Important**: Add your bot as an administrator to your target channel before running the app.

#### Finding Your Chat ID

For a **channel**:
1. Add your bot to the channel and make it an admin.
2. Send any message to the channel.
3. Open `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in a browser (replace `<YOUR_BOT_TOKEN>` with your actual token).
4. Look for `"chat":{"id":-1002024351434,"title":"Your Channel Name"}` — the `id` is your chat ID.

For a **private chat** (testing):
1. Open Telegram and search for **@userinfobot**.
2. Send `/start` — it will reply with your numeric User ID.

#### Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/).
2. Sign in or create an account.
3. Navigate to [API Keys](https://platform.openai.com/api-keys).
4. Click **"Create new secret key"** and copy the generated key (starts with `sk-`).
5. Paste it as `OPENAI_API_KEY` in your `.env` file.
6. **Note**: Ensure your account has sufficient credits. If you see `Error code: 429 - insufficient_quota`, visit [Billing Settings](https://platform.openai.com/account/billing) to add funds.

#### Getting the SID Cookie

1. Open [https://www.business-standard.com/](https://www.business-standard.com/) in your browser.
2. Accept cookies if prompted.
3. Open Developer Tools (**F12** or **Cmd+Option+I** on macOS).
4. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox).
5. Under **Cookies** → `www.business-standard.com`, find the `_sid` cookie.
6. Copy its value and paste it as `SID` in your `.env` file.
7. **Note**: This cookie expires periodically. If scraping fails, refresh the page and get a new `_sid` value.

### 3. Example `.env` File

```env
TELEGRAM_BOT_TOKEN="6186948996:AAESaHBK8TGiu8PyXD1CI354EQ3IdLyH9rs"
TELEGRAM_CHAT_ID="-1002024351434"
OPENAI_API_KEY="sk-proj-your-api-key-here"
SID="your_sid_cookie_value_here"
```

> ⚠️ **Security**: Never commit `.env` to version control. It is already listed in `.gitignore`.

## Usage

### Build and Run

```sh
# Build the Docker image
make build

# Run the scraper
make run
```

### Full Rebuild (after code changes)

```sh
make rebuild
```

### Other Commands

| Command | Description |
|---------|-------------|
| `make build` | Build the Docker image |
| `make run` | Run the scraper once |
| `make up` | Start the container in background |
| `make down` | Stop and remove the container |
| `make rebuild` | Full rebuild: stop → build → start |
| `make sh` | Open interactive shell inside the container |

## Logs

- **Application log**: `scrap/storage/scrap.log`
- **Console output**: Printed during `make run`

## State Files

The app tracks processed articles in `scrap/storage/`:

| File | Purpose |
|------|---------|
| `saved_date.txt` | Timestamp of the last processed article |
| `sent_urls.txt` | List of recently sent article URLs (last 10) |

These files are auto-created on first run.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Business   │ ──▶ │  Web Scraper     │ ──▶ │  OpenAI GPT     │
│  Standard   │     │  (BeautifulSoup)  │     │  (Hindi Trans.) │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
                                               ┌─────────────────┐
                                               │  Telegram Bot   │
                                               │  API Client     │
                                               └────────┬────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Telegram       │
                                               │  Channel        │
                                               └─────────────────┘
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'PIL'` | Missing dependencies | Run `make rebuild` |
| `SID environment variable is not set` | `.env` missing or `SID` empty | Check `scrap/.env` has a valid `SID` |
| `Error code: 401 - Incorrect API key` | Invalid OpenAI key | Verify `OPENAI_API_KEY` in `.env` |
| `Error code: 429 - insufficient_quota` | OpenAI account out of credits | Add funds at [OpenAI Billing](https://platform.openai.com/account/billing) |
| `Response status: 404 - Not Found` | Invalid Telegram token or chat ID | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| `Failed to fetch the page. Status code: 403` | SID cookie expired | Get a fresh `_sid` from Business Standard |

## Development

```sh
# Enter the container shell
make sh

# Install additional packages inside the container
pip install <package_name>
```
