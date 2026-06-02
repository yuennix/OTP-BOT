# OTP-BOT

A Telegram bot that monitors multiple SMS APIs and forwards incoming OTPs to a Telegram group with an interactive user interface.

## Features

- Get Number — assigns a virtual phone number from the SMS pool
- Change Number — swap to a different number instantly
- Change Country — filter numbers by country
- Status — check the latest OTP received on your number
- Live Traffic — see the last 10 OTPs across all numbers
- Auto-forward — every new OTP is posted to your Telegram group automatically

## Setup

1. Clone this repo
2. Install dependencies:
   pip install "python-telegram-bot[job-queue]" requests urllib3
3. Set these environment variables:
   - BOT_TOKEN
   - TARGET_CHAT
   - API1_TOKEN
   - API2_TOKEN
   - API3_KEY
   - GROUP_LINK (optional, your Telegram group invite link)
4. Run:
   python bot/main.py
