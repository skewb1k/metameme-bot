include .env

run:
	BOT_TOKEN=${BOT_TOKEN} CHANNEL_ID=${CHANNEL_ID} METAMEME_INTERVAL=${METAMEME_INTERVAL} python main.py

venv:
	python3 -m venv .venv \
	&& source .venv/bin/activate \

install:
	pip install -r requirements.txt

.PHONY: run venv install