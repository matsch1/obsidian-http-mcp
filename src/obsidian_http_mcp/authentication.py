from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import get_http_request
from dotenv import load_dotenv

import os

# ------------------------
# Load environment
# ------------------------
load_dotenv()

MCP_API_KEY = os.getenv("MCP_API_KEY")
MCP_USER = os.getenv("MCP_USER")


# ------------------------
# Authentication Middleware
# ------------------------
class UserAuthMiddleware(Middleware):
    async def on_list_tools(self, context: MiddlewareContext, call_next):
        request = get_http_request()
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ToolError("Access denied: missing Authorization header")

        token = auth_header.removeprefix("Bearer ").strip()
        if token != MCP_API_KEY:
            raise ToolError("Access denied: invalid token")

        return await call_next(context)

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        request = get_http_request()

        # Expect header like: Authorization: Bearer <token>
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise ToolError("Access denied: missing Authorization header")

        token = auth_header.removeprefix("Bearer ").strip()
        user_id = await self.verify_token_and_get_user_id(token)

        if not user_id:
            raise ToolError("Access denied: invalid token")

        # Store user info in context state
        context.fastmcp_context.set_state("user_id", user_id)

        return await call_next(context)

    async def verify_token_and_get_user_id(self, token: str) -> str | None:
        return MCP_USER if token == MCP_API_KEY else None
