docker build -t mcp .
docker run -d \
  --name mcp \
  -p 9001:9001 \
  mcp
