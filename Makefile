cf = -f infra/docker/docker-compose.yml
pf = -p scrap-news

build:
	docker compose $(cf) $(pf) build
up:
	docker compose $(cf) up -d
down:
	docker compose $(cf) down --remove-orphans
run:
	docker compose $(cf) $(pf) run --rm scrappy