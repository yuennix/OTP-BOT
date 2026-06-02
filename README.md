# OTP-BOT

A Telegram bot that monitors multiple SMS APIs and forwards incoming OTPs to a Telegram group.

## Features
- \ud83d\udcf1 **Get Number** \u2014 assigns a virtual phone number from the SMS pool
- \ud83d\udd04 **Change Number** \u2014 swap to a different number
- \ud83c\udf0d **Change Country** \u2014 filter numbers by country
- \ud83d\udcca **Status** \u2014 check the latest OTP received on your number
- \ud83d\udd34 **Live Traffic** \u2014 see the last 10 OTPs across all numbers
- \ud83d\udce2 **Auto-forward** \u2014 every new OTP is posted to your Telegram group

## Setup
1. Clone this repo
2. Install dependencies: `pip install "python-telegram-bot[job-queue]" requests urllib3`
3. Set environment variables: `BOT_TOKEN`, `TARGET_CHAT`, `API1_TOKEN`, `API2_TOKEN`, `API3_KEY`
4. Run: `python bot/main.py`
