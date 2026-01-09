# Foursquare Places MCP Server (Python)

A Python MCP server for the [Foursquare Places API](https://location.foursquare.com/places/), providing location search and place details. Built with the [Dedalus MCP framework](https://github.com/dedalus-labs/dedalus-mcp-python).

## Features

- **search_near** - Search for places near a location query
- **search_near_point** - Search for places near coordinates
- **place_snap** - Find the most likely place at coordinates
- **place_details** - Get detailed information about a place
- **get_location** - Get coordinates for a location query

## Installation

```bash
# Clone the repository
git clone https://github.com/dedalus-labs/foursquare-places-mcp-python.git
cd foursquare-places-mcp-python

# Install dependencies with uv
uv sync
```

## Configuration

Create a `.env` file with your Foursquare API key:

```bash
FOURSQUARE_API_KEY=your_api_key_here
```

Get your API key from [Foursquare Developer](https://location.foursquare.com/developer/).

## Usage

### Running the Server

```bash
uv run python src/main.py
```

The server will start on `http://localhost:3015/mcp`.

### Testing with the Client

```bash
uv run python src/client.py
```

## Tools

### search_near

Search for places near a location.

**Parameters:**
- `query` (required): What to search for (e.g., "coffee", "pizza")
- `near` (required): Location to search near (e.g., "San Francisco, CA")
- `limit` (optional): Number of results (default: 10)

### search_near_point

Search for places near specific coordinates.

**Parameters:**
- `query` (required): What to search for
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate
- `limit` (optional): Number of results (default: 10)

### place_snap

Find the most likely place at a location.

**Parameters:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate

### place_details

Get detailed information about a specific place.

**Parameters:**
- `fsq_id` (required): Foursquare place ID

### get_location

Get coordinates for a location query.

**Parameters:**
- `near` (required): Location to geocode (e.g., "New York, NY")

## License

MIT
