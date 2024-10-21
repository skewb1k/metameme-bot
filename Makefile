include .env

.PHONY: run
run:
	BOT_TOKEN=${BOT_TOKEN} python main.py