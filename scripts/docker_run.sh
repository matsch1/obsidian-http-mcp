# Load .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# docke$stuff
docker build -t mcp:latest .

docker run -d \
  --name obsidian-http-mcp \
  --network mcp \
  -v $VAULT_PATH:/vault \
  -e MCP_API_KEY=$MCP_API_KEY \
  -e MCP_USER=$MCP_USER \
  -p 9001:9001 \
  --restart unless-stopped \
  mcp:latest
