# Load .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# docke$stuff
docker build -t mcp:latest .

docker run -d \
  --name mcp \
  -v $VAULT_PATH:/vault \
  --env-file .env \
  -p 9001:9001 \
  mcp:latest
