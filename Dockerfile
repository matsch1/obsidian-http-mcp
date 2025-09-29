FROM smrati/python-uv-slim-bookworm:3.13

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y vim-tiny curl && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy the source directory (with pyproject.toml)
COPY . /app

# Install dependencies via Poetry
RUN poetry install --no-root

# Environment variable
ENV VAULT_PATH=/vault

# Run the server via Poetry
CMD ["poetry", "run", "python", "src/obsidian_http_mcp/server.py", "--transport", "tcp", "--host", "0.0.0.0", "--port", "9001"]
