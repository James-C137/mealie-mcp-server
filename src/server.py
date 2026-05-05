import logging
import os
import traceback

from dotenv import load_dotenv
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from pydantic import AnyHttpUrl

from auth import WorkOSTokenVerifier
from mealie import MealieFetcher
from prompts import register_prompts
from tools import register_all_tools

# Load environment variables first
load_dotenv()

# Get log level from environment variable with INFO as default
log_level_name = os.getenv("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_name.upper(), logging.INFO)

# Configure logging
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("mealie_mcp_server.log")],
)
logger = logging.getLogger("mealie-mcp")

MEALIE_BASE_URL = os.getenv("MEALIE_BASE_URL")
MEALIE_API_KEY = os.getenv("MEALIE_API_KEY")
WORKOS_ISSUER = os.getenv("WORKOS_ISSUER")
MCP_RESOURCE_URL = os.getenv("MCP_RESOURCE_URL")
if not MEALIE_BASE_URL or not MEALIE_API_KEY:
    raise ValueError(
        "MEALIE_BASE_URL and MEALIE_API_KEY must be set in environment variables."
    )
if not WORKOS_ISSUER or not MCP_RESOURCE_URL:
    raise ValueError(
        "WORKOS_ISSUER and MCP_RESOURCE_URL must be set in environment variables."
    )

mcp = FastMCP(
    "mealie",
    host=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", "8000")),
    token_verifier=WorkOSTokenVerifier(
        issuer=WORKOS_ISSUER,
        resource=MCP_RESOURCE_URL,
    ),
    auth=AuthSettings(
        issuer_url=AnyHttpUrl(WORKOS_ISSUER),
        resource_server_url=AnyHttpUrl(MCP_RESOURCE_URL),
        required_scopes=[],
    ),
)

try:
    mealie = MealieFetcher(
        base_url=MEALIE_BASE_URL,
        api_key=MEALIE_API_KEY,
    )
except Exception as e:
    logger.error({"message": "Failed to initialize Mealie client", "error": str(e)})
    logger.debug({"message": "Error traceback", "traceback": traceback.format_exc()})
    raise

register_prompts(mcp)
register_all_tools(mcp, mealie)

if __name__ == "__main__":
    try:
        logger.info({"message": "Starting Mealie MCP Server"})
        mcp.run(transport="streamable-http")
    except Exception as e:
        logger.critical(
            {"message": "Fatal error in Mealie MCP Server", "error": str(e)}
        )
        logger.debug(
            {"message": "Error traceback", "traceback": traceback.format_exc()}
        )
        raise
