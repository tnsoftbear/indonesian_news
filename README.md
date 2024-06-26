# Scrap Bot

This application do the following:

* Scraps news from [Business Standard](https://www.business-standard.com/) with image.
* Translates text into Hindi and adjust it to conform requirements of Telegram post.
* Posts it to Telegram channel.

## Installation

1) Make sure you have `make` tool installed:

* `xcode-select --install` for MacOS.
* `sudo apt-get install build-essential` for Linux.

2) Run `make build` for building docker container.

3) Open `www.business-standard.com`, confirm cookies and get `_sid` cookie value from Dev Tools.

4) Rename `/scrap/.env-sample` to `/scrap/.env` and fill the variables.

5) Run `make run`

## Logs

`/scrap/storage/scrap.log`

## Development

```sh
# Enter container
docker run -it -v ./scrap:/scrap scrap-news-scrappy sh
```