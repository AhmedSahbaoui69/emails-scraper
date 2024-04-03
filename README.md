# Email Scraper Discord Bot
![logo](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flogodownload.org%2Fwp-content%2Fuploads%2F2017%2F11%2Fdiscord-logo-16.png&f=1&nofb=1&ipt=89abe9fb5a1e89f622024e2e9a0b89f1e1e75e8e0d64785678bba4f98b2d9cb4&ipo=images)

## Description

This repository contains a collection of email scrapers accessible via commands on a Discord bot.

## Installation

### Before You Begin:
- Follow the [Discord Bot documentation](https://discord.com/developers/docs/intro) to create a Discord application and obtain your bot token.
- To run the bot, it needs to be hosted on a server. I recommend using a service like [Heroku](https://www.heroku.com/) or [replit.com](https://replit.com/~) for hosting.



### 1. Clone the Repository

```bash
git clone https://github.com/AhmedSahbaoui69/emails-scraper.git
cd emails-scraper
```
### 2. Install Dependencies

Ensure you have Python and pip installed. Then, run the following command to install the project dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Add add the following environment variable to your shell:

```bash
TOKEN=your_discord_bot_token
```

## How to Use

```bash
/domain_name <querry>
```
Supported websites :
- arbeitsagentur.de
- ausbildung.de
- hotelcareer.de

## License

This project is licensed under the [MIT License](LICENSE).
