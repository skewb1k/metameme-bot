include .env

.PHONY: run
run:
	BOT_TOKEN=${BOT_TOKEN} CHANNEL_ID=${CHANNEL_ID} python main.py