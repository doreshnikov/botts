poetry-export:
	poetry export -f requirements.txt --output requirements.txt

update-tgutils:
	cd aiogram-utils && git pull origin main
	pip install ./aiogram-utils

update: update-tgutils
	poetry update

build: update
	docker compose build

icount := 5
invokers: build
	docker compose down
	docker compose up --scale invoker=${icount} -d

debug := 0
run: invokers
	DEBUG=${debug} python -m botts.bot.main
