FROM python:3.12-slim

ENV POETRY_VERSION=1.6.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Add poetry binary to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 -

# Install the AWS Lambda runtime interface client (I think this just makes it so we can use 3.12-slim with lambda)
RUN pip install awslambdaric

# Set the working directory in the container
WORKDIR /app

# Copy in python depenedncy requirements & install
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

# Copy everything else in (separate from bringing in the depenedncies for docker caching efficiency - or something like that)
COPY . /app

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]

CMD ["python", "main.py"]
