# custom variables
SHELL = /bin/bash
COMPOSE_CMD = docker compose -f ./docker-compose.yml

# shortcuts
up:
	$(COMPOSE_CMD) up --build -d

down:
	$(COMPOSE_CMD) down --remove-orphans

clear:
	$(COMPOSE_CMD) down --remove-orphans -v

# db
make_migrations:
	$(COMPOSE_CMD) exec app alembic -c /app/src/db/alembic.ini revision --autogenerate || true

migrate:
	$(COMPOSE_CMD) exec app alembic -c /app/src/db/alembic.ini upgrade head || true

create_default_users:
	$(COMPOSE_CMD) exec -it app bash -c "python manage.py create_default_users"

delete_all_orders:
	$(COMPOSE_CMD) exec -it app bash -c "python manage.py delete_all_orders"

.PHONY: up down clear make_migrations migrate create_default_users delete_all_orders
