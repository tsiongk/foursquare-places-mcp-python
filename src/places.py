# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Foursquare Places API operations for MCP server.

Required environment variables:
    FOURSQUARE_API_KEY: Foursquare Places API key

API Documentation:
    https://docs.foursquare.com/
"""

import os
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

from dedalus_mcp import tool


load_dotenv()

# Read API key from environment
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY", "")
FOURSQUARE_BASE_URL = "https://api.foursquare.com/v3"


# --- Response Models ---------------------------------------------------------


class PlacesResult(BaseModel):
    """Generic Foursquare Places API result."""

    success: bool
    data: Any = None
    error: str | None = None


# --- Helper ------------------------------------------------------------------


async def _request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
) -> PlacesResult:
    """Make a request to Foursquare Places API.

    Args:
        method: HTTP method (GET, POST)
        path: API path
        params: Query parameters

    Returns:
        PlacesResult with success status and data or error.
    """
    if not FOURSQUARE_API_KEY:
        return PlacesResult(success=False, error="FOURSQUARE_API_KEY environment variable not set")

    url = f"{FOURSQUARE_BASE_URL}{path}"
    headers = {
        "Authorization": FOURSQUARE_API_KEY,
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            else:
                response = await client.post(url, headers=headers, json=params, timeout=30.0)
            
            if response.status_code == 429:
                return PlacesResult(success=False, error="Rate limited. Please try again later.")
            if response.status_code == 401:
                return PlacesResult(success=False, error="Unauthorized. Check your API key.")
            
            response.raise_for_status()
            return PlacesResult(success=True, data=response.json())
    except Exception as e:
        return PlacesResult(success=False, error=str(e))


def _format_place(place: dict[str, Any]) -> dict[str, Any]:
    """Format a place result for cleaner output."""
    location = place.get("location", {})
    categories = place.get("categories", [])
    
    return {
        "fsq_id": place.get("fsq_id"),
        "name": place.get("name"),
        "address": location.get("formatted_address", location.get("address")),
        "locality": location.get("locality"),
        "region": location.get("region"),
        "country": location.get("country"),
        "distance": place.get("distance"),
        "categories": [c.get("name") for c in categories],
        "latitude": location.get("latitude") if "latitude" in place.get("geocodes", {}).get("main", {}) else None,
        "longitude": location.get("longitude") if "longitude" in place.get("geocodes", {}).get("main", {}) else None,
    }


# --- Foursquare Places Tools -------------------------------------------------


@tool(
    description=(
        "Search for places near a particular named region using Foursquare Places API. "
        "Returns places with details like name, address, categories, and distance. "
        "Best for queries like 'coffee shops near Times Square'."
    )
)
async def search_near(
    where: str,
    what: str,
    limit: int = 5,
) -> PlacesResult:
    """Search for places near a named location.

    Args:
        where: A geographic region (e.g., 'Los Angeles', 'Times Square', 'Brooklyn').
        what: What to look for (e.g., 'coffee shop', 'pizza', 'gym', 'hotel').
        limit: Number of results to return (1-50, default 5).

    Returns:
        PlacesResult with matching places.
    """
    limit = max(1, min(limit, 50))

    params = {
        "query": what,
        "near": where,
        "limit": limit,
    }

    result = await _request("GET", "/places/search", params)
    
    if result.success and result.data:
        places = result.data.get("results", [])
        result.data = {
            "query": what,
            "location": where,
            "count": len(places),
            "places": [_format_place(p) for p in places],
        }
    
    return result


@tool(
    description=(
        "Search for places near specific latitude/longitude coordinates. "
        "More precise than searching by named region. "
        "Best for queries when you have exact coordinates."
    )
)
async def search_near_point(
    what: str,
    ll: str,
    radius: int = 1000,
    limit: int = 5,
) -> PlacesResult:
    """Search for places near coordinates.

    Args:
        what: What to look for (e.g., 'coffee shop', 'pizza').
        ll: Comma-separated lat,lng (e.g., '40.74,-74.0').
        radius: Search radius in meters (default 1000).
        limit: Number of results to return (1-50, default 5).

    Returns:
        PlacesResult with matching places.
    """
    limit = max(1, min(limit, 50))
    radius = max(1, min(radius, 100000))

    params = {
        "query": what,
        "ll": ll,
        "radius": radius,
        "limit": limit,
    }

    result = await _request("GET", "/places/search", params)
    
    if result.success and result.data:
        places = result.data.get("results", [])
        result.data = {
            "query": what,
            "coordinates": ll,
            "radius_meters": radius,
            "count": len(places),
            "places": [_format_place(p) for p in places],
        }
    
    return result


@tool(
    description=(
        "Get the most likely place the user is at based on their location coordinates. "
        "Uses Foursquare's Place Snap technology. Ideal for 'where am I?' queries."
    )
)
async def place_snap(
    ll: str,
    limit: int = 1,
) -> PlacesResult:
    """Identify the most likely place at coordinates.

    Args:
        ll: Comma-separated lat,lng of user's location (e.g., '40.74,-74.0').
        limit: Number of candidate places to return (1-10, default 1).

    Returns:
        PlacesResult with most likely places.
    """
    limit = max(1, min(limit, 10))

    params = {
        "ll": ll,
        "limit": limit,
    }

    result = await _request("GET", "/places/nearby", params)
    
    if result.success and result.data:
        places = result.data.get("results", [])
        result.data = {
            "coordinates": ll,
            "count": len(places),
            "places": [_format_place(p) for p in places],
        }
    
    return result


@tool(
    description=(
        "Get comprehensive details about a specific place using its Foursquare ID (fsq_id). "
        "Includes description, contact info, hours, rating, price, photos, and reviews."
    )
)
async def place_details(
    fsq_id: str,
    fields: str | None = None,
) -> PlacesResult:
    """Get detailed information about a place.

    Args:
        fsq_id: Foursquare place ID obtained from search results.
        fields: Comma-separated list of fields to include (optional).

    Returns:
        PlacesResult with place details.
    """
    params = {}
    if fields:
        params["fields"] = fields
    else:
        params["fields"] = "name,location,categories,description,tel,website,hours,rating,price,photos,tips"

    result = await _request("GET", f"/places/{fsq_id}", params)
    
    if result.success and result.data:
        place = result.data
        result.data = {
            "fsq_id": fsq_id,
            "name": place.get("name"),
            "description": place.get("description"),
            "location": place.get("location"),
            "categories": [c.get("name") for c in place.get("categories", [])],
            "contact": {
                "phone": place.get("tel"),
                "website": place.get("website"),
            },
            "hours": place.get("hours"),
            "rating": place.get("rating"),
            "price": place.get("price"),
            "photos": place.get("photos", {}).get("groups", []),
            "tips": [t.get("text") for t in place.get("tips", [])[:5]],
        }
    
    return result


@tool(
    description=(
        "Get user's approximate location based on their IP address. "
        "Useful when the user hasn't provided their precise location."
    )
)
async def get_location() -> PlacesResult:
    """Get approximate location from IP.

    Returns:
        PlacesResult with approximate coordinates.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://ipapi.co/json/", timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            lat = data.get("latitude")
            lng = data.get("longitude")
            
            if lat and lng:
                return PlacesResult(
                    success=True,
                    data={
                        "coordinates": f"{lat},{lng}",
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "country": data.get("country_name"),
                        "note": "This is an approximation based on IP address.",
                    },
                )
            else:
                return PlacesResult(success=False, error="Could not determine location from IP.")
    except Exception as e:
        return PlacesResult(success=False, error=f"Location lookup failed: {e}")


# --- Export ------------------------------------------------------------------

places_tools = [
    search_near,
    search_near_point,
    place_snap,
    place_details,
    get_location,
]
