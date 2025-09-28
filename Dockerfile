FROM smrati/python-uv-slim-bookworm:3.13

WORKDIR /app

RUN apt-get update && \
    apt-get install -y vim-tiny && \
    rm -rf /var/lib/apt/lists/*

RUN pip install fastmcp python-dotenv

COPY src/obsidian_http_mcp /app

ENV VAULT_PATH=/vault

CMD ["python", "server.py", "--transport", "tcp", "--host", "0.0.0.0", "--port", "9001"]
