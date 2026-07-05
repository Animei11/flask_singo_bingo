.PHONY: setup freeze test debug kill eb format
PYTHON := .venv/bin/python
FLASK  := .venv/bin/flask
PIP := .venv/bin/pip
# APP_URL := http://127.0.0.1:5000//db/testGame
APP_URL1 := http://127.0.0.1:5000/startGame/TESTS
APP_URL2 := http://127.0.0.1:5000/bingoCard/TESTS
# Initial setup
setup:
	@echo "STARTING: Creating .venv"
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	@echo "STARTING: Installing dependencies"
	$(PIP) install -r requirements.txt
	@test -f .env || touch .env
	@echo "DONE: Setup .venv and installed dependencies."

# Update requirements.txt with dependencies in .venv
freeze:
	@echo "Starting: Updating requirements.txt"
	$(PIP) freeze > requirements.txt
	@echo "DONE: requirements.txt updated."

# Testing without running Flask
test:
	$(PYTHON) -m pytest

# So I don't have to use the GUI anymore to debug
debug:
	@lsof -ti:5000 | xargs kill || true
	@echo "🚀 Starting Flask (debug + reload)..."
	FLASK_APP=app.py \
	FLASK_ENV=development \
	FLASK_DEBUG=1 \
	$(FLASK) run --reload --debugger &
	@sleep 1
# 	@echo "Creating GAMESTATE: TESTS"
# 	@$(PYTHON) -m webbrowser $(APP_URL)
	@echo "Loading spotify player for TESTS..."
	@$(PYTHON) -m webbrowser $(APP_URL1)
	@echo "Loading bingo card for TESTS..."
	@$(PYTHON) -m webbrowser $(APP_URL2)
	@wait

# Test with vercel before deploying
vercel:
	@echo "Starting: Vercel local run"
	npx vercel dev
	@echo "DONE: Vercel local run complete."

# So I don't have to use the GUI anymore to debug
kill:
	@lsof -ti:5000 | xargs kill || true
	@echo "Killed debugger"

# TODO: AWS EB
eb:
	@echo "Starting: AWS Elastic Beanstalk local run"
# 	eb local run
	@echo "DONE: AWS Elastic Beanstalk local run complete."

# TODO: Code formatter checker
format:
	@echo "Starting: Code format check"
# 	black --check app/
	@echo "DONE: Code format check complete."