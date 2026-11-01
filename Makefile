# Variables (override on the command line, e.g. `make play AB=off`)
AB      ?= on
GAMES   ?= 10
FIRST   ?= human
SYMBOL  ?= X
NODELAY ?=
UI      ?= auto
# simulate / compare print plain text so the output stays in the terminal
REPORT_UI ?= console

RUN  = docker compose run --rm app
NODELAY_FLAG = $(if $(NODELAY),--no-delay,)

.PHONY: help build run play simulate compare test lint check shell clean

help: ## Show this help
	@echo "Targets:"
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'
	@echo ""
	@echo "Variables: AB=on|off GAMES=N FIRST=human|ai SYMBOL=X|O NODELAY=1 UI=console|curses"

build: ## Build the Docker image
	docker compose build

run: ## Interactive menu
	$(RUN) python -m tictactoe --ui $(UI)

play: ## Play vs AI (AB, FIRST, SYMBOL)
	$(RUN) python -m tictactoe --ui $(UI) --mode play --alpha-beta $(AB) --first $(FIRST) --symbol $(SYMBOL)

simulate: ## AI vs AI (GAMES, AB, NODELAY)
	$(RUN) python -m tictactoe --ui $(REPORT_UI) --mode simulate --alpha-beta $(AB) --games $(GAMES) $(NODELAY_FLAG)

compare: ## Compare minimax with and without alpha-beta
	$(RUN) python -m tictactoe --ui $(REPORT_UI) --mode compare

test: ## Run pytest with coverage
	$(RUN) pytest --cov=tictactoe --cov-report=term-missing

lint: ## Run flake8
	$(RUN) flake8

check: lint test ## Lint + test

shell: ## Bash inside the container
	$(RUN) bash

clean: ## Remove containers and caches
	docker compose down --remove-orphans
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .coverage
