# Stash MCP Server

MCP (Model Context Protocol) server that exposes advanced tools for querying a Stash instance with complex filtering capabilities, optimized caching, intelligent analysis, and personalized recommendations.

### Prompts
| Prompt                | Description                               | Parameters            |
| --------------------- | ----------------------------------------- | --------------------- |
| `analyze-performer`   | Complete performer analysis with insights | `performer_name: str` |
| `library-insights`    | Strategic insights for the entire library | —                     |
| `recommend-scenes`    | Personalized scene recommendations        | `preferences: str`    |
| `discover-performers` | Performer discovery by criteria           | `criteria: str`       |

### Tools
| Tool                            | Description                                  | Parameters                                                                     |
| ------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------ |
| `advanced_performer_analysis`   | Deep analysis with progress and logging      | `performer_name: str`, `include_similar: bool`, `deep_scene_analysis: bool`    |
| `batch_performer_insights`      | Aggregated insights from multiple performers | `performer_names: List[str]`, `max_performers: int`                            |
| `health_check`                  | Basic connectivity/cache status              | —                                                                              |
| `get_performer_info`            | Detailed performer information               | `performer_name: str`                                                          |
| `get_all_performers`            | List performers with advanced filtering      | `favorites_only: bool=True`, advanced filters (see "Advanced Filters" section) |
| `get_all_scenes_from_performer` | Scenes for a performer                       | `performer_name: str`, `organized_only: bool=True`                             |
| `get_all_scenes`                | List all scenes with optional filters        | advanced filters (see "Advanced Filters" section)                              |

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

## Environment Variables
| Variable                      | Default                 | Description                                                     |
| ----------------------------- | ----------------------- | --------------------------------------------------------------- |
| `STASH_ENDPOINT`              | `http://localhost:6969` | Stash server endpoint (scheme, host y puerto juntos)            |
| `STASH_API_KEY`               | —                       | Required API key (mandatory, if missing the server won't start) |
| `STASH_CONNECT_RETRIES`       | `3`                     | Initial connection retries                                      |
| `STASH_CONNECT_DELAY_SECONDS` | `1.5`                   | Delay between retries (seconds)                                 |
| `LOG_LEVEL`                   | `INFO`                  | Log level: DEBUG, INFO, WARNING, ERROR                          |


## Running
### Local (stdio, default)
```bash
python server.py
```

### HTTP (optional, uncomment in `main`)
```python
# mcp.run(transport="http", host="0.0.0.0", port=9001)
```

### Docker (example)
```bash
docker build -t stash_mcp_server:latest .
docker run --rm -e STASH_ENDPOINT=http://host.docker.internal:6969 -e STASH_API_KEY=XXX stash_mcp_server:latest
```

## Technical Notes
- Connection to Stash is performed with configurable retries.
- If the API key is missing, the server generates an error and does not start.
- GraphQL fragments used by queries are centralized in the code (`FRAGMENTS`).
- **Improved cache architecture**: Cache functions are separated from MCP decorators to avoid conflicts with Pydantic schema generation.
- **Advanced filtering**: Robust filter system with modifiers and range handling for complex queries.
- **Enhanced logging**: Detailed information about active filters and query results for better debugging.