import logging
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from codemash_mcp.codemash import CodeMashDataReader

from .utils import (
    McpRunner,
    _force_json_logging,
)

_force_json_logging()

from fastmcp import FastMCP  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402


logger = logging.getLogger(__name__)


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="codemash_",
        env_file=os.getenv("CODEMASH_ENV_FILE", ".env.codemash"),
        env_file_encoding="utf-8",
    )

    data_file: Path = Field(
        default=Path("data/endpoint-3.json"),
        description="The location of the CodeMash data file to use.",
    )


def _init_mcp_server():
    cfg = Config()  # pyright: ignore[reportCallIssue]
    logger.debug(f"Loaded configuration: {cfg.model_dump_json()}")

    # STEP: 1 - Init FastMCP & provide base instructions
    # create & register tools
    mcp = FastMCP(
        name="CodeMash 2026 Conference MCP",
        instructions="""A set of tools that can be used for retrieving information about the CodeMash 2026 conference,
            including sessions, speakers, and schedules.
        
            CodeMash is a unique event that educates developers on current practices, methodologies and technology
            trends in a variety of platforms and development languages. Held every January at the lush Kalahari Resort
            in Sandusky, Ohio, attendees will be able to attend a world-class technical conference amid the US's
            largest indoor waterpark. Nobody will frown if you show up in shorts, sandals, and your loudest t-shirt.
            You might even win a prize for doing so.
            
            It's not just about a grind of sessions, but also providing attendees the opportunity of continuing
            the conversations and networking outside of the daily conference events. The goal has always been to
            achieve this mission by creating a conference environment that focuses on professionalism and respect
            for one another.
            
            CodeMash strives to motivate attendees through amazing speakers and incredible content. Previous 
            speakers have included Mary Poppendeick, Scott Guthrie, Neal Ford, Scott Chacon, and Chad Fowler. 
            Sessions over the years have included everything from F# to JavaScript, mobile application development,
            career skills, software development processes, and so much more! There are also two days worth of
            hands-on workshops covering everything from test driven development to improving your communication
            skills to augment the two basic days of sessions.""",
    )

    # STEP: 4 - Register tools
    code_mash = CodeMashDataReader(cfg.data_file)
    mcp.tool(code_mash.event)
    mcp.tool(code_mash.hotels)
    mcp.tool(code_mash.speakers)
    mcp.tool(code_mash.sessions)
    mcp.tool(code_mash.rooms)
    mcp.tool(code_mash.tracks)
    mcp.tool(code_mash.venue)

    # register health check
    @mcp.custom_route("/health", ["GET"])
    async def health_check(response):
        return JSONResponse({"status": "OK"})

    return McpRunner(mcp)


server = _init_mcp_server()
