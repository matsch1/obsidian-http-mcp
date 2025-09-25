FROM smrati/python-uv-slim-bookworm:3.13

WORKDIR /app

RUN pip install fastmcp python-dotenv

COPY . /app

ENV VAULT_PATH=/vault

CMD ["python", "server.py", "--transport", "tcp", "--host", "0.0.0.0", "--port", "9001"]
