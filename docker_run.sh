docker build -t mcp .
docker run -d \
  --name mcp \
  -v /mnt/c/Users/maschaefer/obsidian/main:/vault \
  -p 9001:9001 \
  mcp
