# Ponemos el alias a la imagen para referenciarla más adelante
FROM python:3.11-slim AS base

# Creamos y nos movemos a la carpeta trabajo
WORKDIR /app

# Instalamos poetry
RUN pip install poetry==2.1.1

# Copiamos archivos de configuración en la carpeta /app
COPY poetry.lock pyproject.toml README.md ./

# Copiamos el código fuente de su aplicación a la carpeta /app/src
COPY src/ src/

# Deshabilitamos el ambiente virtual de poetry
RUN poetry config virtualenvs.create false

# Instalamos las dependencias de producción (no de desarrollo)
RUN poetry install --only main

# Creamos un nuevo stage con el alias runner (tenga presente este nombre)
FROM python:3.11-slim AS runner

# Definimos la misma carpeta de trabajo
WORKDIR /app

# Copiamos las librerías instaladas y los archivos necesarios de base a runner
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copiamos el código de la aplicación
COPY --from=base /app/src/ /app/src/

# Modificamos variables de ambiente para la ejecución
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# ============================================
# Configuración de New Relic APM
# ============================================
# Nombre de la aplicación en New Relic dashboard
ENV NEW_RELIC_APP_NAME="Blacklist-API"
# Enviar logs a stdout para Docker/ECS
ENV NEW_RELIC_LOG=stdout
# Habilitar distributed tracing para mejor observabilidad
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
# Nivel de log (info, debug, warning, error)
ENV NEW_RELIC_LOG_LEVEL=info
# La license key se define en docker-compose o como secret en ECS
# ENV NEW_RELIC_LICENSE_KEY=tu_license_key_aqui

# Expone el puerto 
EXPOSE 9000

# Usamos newrelic-admin como entrypoint para instrumentar la aplicación
ENTRYPOINT ["newrelic-admin", "run-program"]

# Ejecutamos la aplicación en el servidor con New Relic instrumentación
CMD ["uvicorn", "entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "9000"]