.PHONY: help install run docker-up docker-down docker-build docker-logs test clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install       - Instala las dependencias con Poetry"
	@echo "  make docker-build - Construye las imágenes Docker"
	@echo "  make docker-up    - Inicia los servicios con Docker Compose"
	@echo "  make docker-down  - Detiene los servicios Docker"
	@echo "  make docker-logs  - Muestra los logs de los contenedores"
	@echo "  make clean        - Limpia archivos temporales"

install:
	poetry install

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

