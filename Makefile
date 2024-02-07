cf = -f infra/docker/docker-compose.yml
pf = -p scrap-news

build:
	docker compose $(cf) $(pf) build
up:
	docker compose $(cf) $(pf) up -d
down:
	docker compose $(cf) $(pf) down --remove-orphans
rebuild:
	@make down
	@make build
	@make up
run:
	docker compose $(cf) $(pf) run --rm scrappy
sh:
	docker run -it -v ./scrap:/scrap scrap-news-scrappy sh