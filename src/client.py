# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Sample MCP client for testing the Foursquare Places MCP server."""

import asyncio

from dedalus_mcp import MCPClient


SERVER_URL = "http://localhost:3015/mcp"


async def main() -> None:
    client = await MCPClient.connect(SERVER_URL)

    # List tools
    result = await client.list_tools()
    print(f"\nAvailable tools ({len(result.tools)}):\n")
    for t in result.tools:
        print(f"  {t.name}")
        if t.description:
            print(f"    {t.description[:80]}...")
        print()

    # Test get_location
    print("--- get_location ---")
    location = await client.call_tool("get_location", {})
    print(location)
    print()

    # Test search_near
    print("--- search_near ---")
    search_results = await client.call_tool(
        "search_near",
        {"where": "Times Square, New York", "what": "pizza", "limit": 3},
    )
    print(search_results)
    print()

    # Test search_near_point
    print("--- search_near_point ---")
    point_results = await client.call_tool(
        "search_near_point",
        {"what": "coffee", "ll": "40.758,-73.9855", "radius": 500, "limit": 3},
    )
    print(point_results)
    print()

    # Test place_snap
    print("--- place_snap ---")
    snap_results = await client.call_tool(
        "place_snap",
        {"ll": "40.758,-73.9855", "limit": 2},
    )
    print(snap_results)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
