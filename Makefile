# custom variables
SHELL = /bin/bash
COMPOSE_CMD = docker compose -f ./docker-compose.yml

# shortcuts
up:
	$(COMPOSE_CMD) up --build

down:
	$(COMPOSE_CMD) down --remove-orphans

clear:
	$(COMPOSE_CMD) down --remove-orphans -v

# PostgreSQL
delete_all_orders:
	$(COMPOSE_CMD) exec -it app bash -c "python manage.py delete_all_orders"

init_db:
	$(COMPOSE_CMD) exec -it app bash -c "python manage.py init_db"

.PHONY: up down clear delete_all_orders init_db
