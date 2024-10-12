poetry-export:
	poetry export -f requirements.txt --output requirements.txt

update-tgutils:
	cd aiogram-utils && \
		git fetch --all && \
		git reset --hard origin/main
	pip install ./aiogram-utils

update: update-tgutils
	poetry update

build:
	docker compose build

icount := 5
invokers: build
	docker compose down
	docker compose up --scale invoker=${icount} -d

ensure-logs:
	mkdir -p logs

debug := 0
run: invokers
	DEBUG=${debug} python -m botts.bot.main
