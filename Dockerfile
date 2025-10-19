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

# Expone el puerto 
EXPOSE 9000

# Ejecutamos la aplicación en el servidor
CMD ["uvicorn", "entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "9000"]