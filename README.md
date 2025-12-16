# Stash MCP Server

![License](https://img.shields.io/github/license/donlothario/stash_mcp_server)
[![Build](https://github.com/donlothario/stash_mcp_server/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/donlothario/stash_mcp_server/actions/workflows/python-package.yml)
[![Docker image](https://github.com/donlothario/stash_mcp_server/actions/workflows/docker_image.yml/badge.svg?branch=main)](https://github.com/donlothario/stash_mcp_server/actions/workflows/docker_image.yml)
![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdonlothario%2Fstash_mcp_server%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
![Dynamic TOML Badge](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdonlothario%2Fstash_mcp_server%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&query=%24.project.dependencies%5B2%5D&label=dependency)
[![codecov](https://codecov.io/github/donlothario/stash_mcp_server/graph/badge.svg?token=X4YT5BTQPC)](https://codecov.io/github/donlothario/stash_mcp_server)

An MCP (Model Context Protocol) server that provides a concise set of tools to query and analyze an [Stash](https://github.com/stashapp/stash) instance with composable, high‑precision filters, optimized caching for faster queries, automated intelligence for performer/scene analysis, and personalized recommendations based on usage and preferences.

### Prompts
| Prompt                  | Description                               | Parameters            |
| ----------------------- | ----------------------------------------- | --------------------- |
| **analyze-performer**   | Complete performer analysis with insights | `performer_name: str` |
| **library-insights**    | Strategic insights for the entire library | —                     |
| **recommend-scenes**    | Personalized scene recommendations        | `preferences: str`    |
| **discover-performers** | Performer discovery by criteria           | `criteria: str`       |

### Resources
| Resource                    | Description                                     | URI                                       |
| --------------------------- | ----------------------------------------------- | ----------------------------------------- |
| **All performers**          | List of all favorite performers with basic info | `stash://performer/all`                   |
| **Performers Information**  | Detailed information about a specific performer | `stash://performer/{name}`                |
| **Performers by Country**   | List of performers filtered by country          | `stash://performer/country/{country}`     |
| **Performers by Ethnicity** | List of performers filtered by ethnicity        | `stash://performer/ethnicity/{ethnicity}` |
| **Performers Statistics**   | Statistical summary of all performers           | `stash://performer/stats`                 |

### Tools
| Tool                              | Description                                  | Parameters                                                                     |
| --------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------ |
| **advanced_performer_analysis**   | Deep analysis with progress and logging      | `performer_name: str`, `include_similar: bool`, `deep_scene_analysis: bool`    |
| **batch_performer_insights**      | Aggregated insights from multiple performers | `performer_names: List[str]`, `max_performers: int`                            |
| **health_check**                  | Basic connectivity/cache status              | —                                                                              |
| **get_performer_info**            | Detailed performer information               | `performer_name: str`                                                          |
| **get_all_performers**            | List performers with advanced filtering      | `favorites_only: bool=True`, advanced filters (see "Advanced Filters" section) |
| **get_all_scenes_from_performer** | Scenes for a performer                       | `performer_name: str`, `organized_only: bool=True`                             |
| **get_all_scenes**                | List all scenes with optional filters        | advanced filters (see "Advanced Filters" section)                              |

### Advanced Filters for `get_all_performers`

This tool now supports advanced filtering by multiple physical and demographic criteria:

#### Basic Filters
- `favorites_only: bool = True` - Limit to favorite performers
- `country: str` - Filter by country
- `ethnicity: str` - Filter by ethnicity
- `eye_color: str` - Filter by eye color
- `hair_color: str` - Filter by hair color
- `measurements: str` - Filter by body measurements
- `piercings: str` - Filter by piercings
- `tattoos: str` - Filter by tattoos

#### Numeric Filters with Modifiers
- `height_cm: int` - Filter by height in centimeters
- `weight: int` - Filter by weight

#### Filter Modifiers
Each filter supports modifiers for different comparison types:
- `EQUALS` (default) - Exact match
- `NOT_EQUALS` - Not equal
- `GREATER_THAN` - Greater than (numeric only)
- `LESS_THAN` - Less than (numeric only)
- `BETWEEN` - Between two values (numeric only, requires `_value2`)
- `NOT_BETWEEN` - Not between two values (numeric only, requires `_value2`)

#### Range Parameters
For `BETWEEN` and `NOT_BETWEEN` filters:
- `height_cm_value2: int` - Second value for height range
- `weight_value2: int` - Second value for weight range

### Resources for performers information

The server provides dedicated resources to access performers information in multiple formats:

#### Resource URIs

- **`stash://performer/all`** - Lists all favorite performers with basic information
  - Returns: Name, country, ethnicity, height, weight, and associated tags
  - Use case: Get a quick overview of all favorite performers

- **`stash://performer/{name}`** - Detailed information for a specific performer
  - Parameters: `{name}` - Exact performer name
  - Returns: Complete profile including demographics, physical characteristics, bio, and tags
  - Use case: Get comprehensive information about a specific performer

- **`stash://performer/country/{country}`** - Filter performers by country
  - Parameters: `{country}` - Country name or code (e.g., "USA", "ES")
  - Returns: List of performers from the specified country with ethnicity
  - Use case: Discover performers from a specific country

- **`stash://performer/ethnicity/{ethnicity}`** - Filter performers by ethnicity
  - Parameters: `{ethnicity}` - Ethnicity name (e.g., "Caucasian", "Asian")
  - Returns: List of performers with the specified ethnicity and their countries
  - Use case: Find performers matching specific ethnic characteristics

- **`stash://performer/stats`** - Statistical summary of the performer database
  - Returns:
    - Total number of favorite performers
    - Geographic distribution (countries and counts)
    - Ethnic distribution
    - Physical statistics (average height and weight ranges)
  - Use case: Analyze the composition and diversity of your performer collection

## Configuration

The server supports flexible configuration through environment variables:
| Variable                      | Default                 | Description                            |
| ----------------------------- | ----------------------- | -------------------------------------- |
| `STASH_ENDPOINT`              | `http://localhost:6969` | Stash server endpoint                  |
| `STASH_API_KEY`               | —                       | Required API key (mandatory)           |
| `STASH_CONNECT_RETRIES`       | `3`                     | Initial connection retries             |
| `STASH_CONNECT_DELAY_SECONDS` | `1.5`                   | Delay between retries (seconds)        |
| `LOG_LEVEL`                   | `INFO`                  | Log level: DEBUG, INFO, WARNING, ERROR |

### Environment Setup
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```bash
STASH_ENDPOINT=http://localhost:9999
STASH_API_KEY=YOUR_API_KEY
```

## Installation

### Install with uv (recommended)

Clone the repository and install with uv:

```bash
git clone https://github.com/donlothario/stash_mcp_server.git
cd stash_mcp_server
cp .env.example .env
# Edit .env file with your Stash settings
uv sync
```

Or install directly from the repository:

```bash
uv add git+https://github.com/donlothario/stash_mcp_server.git
```

### Install with pip

Install the package in mode:

```bash
git clone https://github.com/donlothario/stash_mcp_server.git
cd stash_mcp_server
cp .env.example .env
# Edit .env file with your Stash settings
python3 -m pip install .
```

Or install directly from the repository:

```bash
python3 -m pip install git+https://github.com/donlothario/stash_mcp_server.git
```

### Docker

#### Build the image
Build the image:

```bash
docker build -t stash_mcp_server:latest .
```

#### Pull the image
Pull the latest image from the Docker registry:

```bash
docker pull ghcr.io/donlothario/stash_mcp_server:latest
```

## Usage

### Running with uv

```bash
uv run stash_mcp_server
```

### Running with pip installation

```bash
python3 -m stash_mcp_server
```

### Configuration example for Claude Desktop/Cursor/VSCode
Add this configuration to your application's settings (mcp.json):

#### Using uv (recommended)
```json
"stash mcp server": {
    "type": "stdio",
    "command": "uv",
    "args": [
      "run",
      "--directory",
      "/path/to/stash_mcp_server",
      "stash_mcp_server"
    ],
    "env": {
        "STASH_ENDPOINT": "http://localhost:9999",
        "STASH_API_KEY": "YOUR_API_KEY",
    }
}
```

#### Using pip installation
```json
"stash mcp server": {
    "type": "stdio",
    "command": "python3",
    "args": [
        "-m",
        "stash_mcp_server"
    ],
    "env": {
        "STASH_ENDPOINT": "http://localhost:9999",
        "STASH_API_KEY": "YOUR_API_KEY",
    }
}
```

#### Using Docker
```json
"stash mcp server": {
    "type": "stdio",
    "command": "docker",
    "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "${workspaceFolder}/.env",
        "ghcr.io/donlothario/stash_mcp_server"
    ]
}
```

## Technical Notes
- Connection to Stash is performed with configurable retries.
- If the API key is missing, the server generates an error and does not start.
- GraphQL fragments used by queries are centralized in the code (`FRAGMENTS`).
- **Improved cache architecture**: Cache functions are separated from MCP decorators to avoid conflicts with Pydantic schema generation.
- **Advanced filtering**: Robust filter system with modifiers and range handling for complex queries.
- **Enhanced logging**: Detailed information about active filters and query results for better debugging.
