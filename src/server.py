# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from places import places_tools


# --- Server ------------------------------------------------------------------

server = MCPServer(
    name="foursquare-places-mcp",
    http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


async def main() -> None:
    server.collect(*places_tools)
    await server.serve(port=3015)
