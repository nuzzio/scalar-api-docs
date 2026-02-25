# CloudBees Unify API Docs (Scalar)

Interactive API reference documentation for the CloudBees Unify platform, powered by [Scalar](https://scalar.com/).

## Quick start

```bash
# Download from GitHub and serve
./serve.sh

# Or use a local OpenAPI spec file
./serve.sh -f /path/to/openapi.yaml
```

This will:

1. Download (or copy) the OpenAPI spec
2. Extract the v3beta and v3 subsets
3. Start a local server at http://localhost:8787

## Usage

```bash
# Default: main branch, port 8787
./serve.sh

# Specific branch
./serve.sh -b develop

# Specific branch and port
./serve.sh -b feature/v3beta-public-api-exploration -p 9090

# Local file (no gh required)
./serve.sh -f ../api/openapiV3/openapi.yaml

# Local file with custom port
./serve.sh -f /path/to/openapi.yaml -p 3000

# Help
./serve.sh -h
```

## Requirements

- **Python 3.x** and **pip3**. Pre-installed on most macOS/Linux systems. If missing: `brew install python3`
- **PyYAML**. Installed automatically by `serve.sh` if missing. Or install manually: `pip3 install pyyaml`
- **GitHub CLI** (`gh`). Only needed if downloading from GitHub. Not needed when using `-f`. Install: `brew install gh`

## What it produces

| Page | URL | Description |
|------|-----|-------------|
| Landing page | http://localhost:8787 | Links to both API references |
| v3beta Public API | http://localhost:8787/v3beta.html | 11 endpoints for external CI/CD integration |
| v3 Platform API | http://localhost:8787/v3.html | 64 endpoints covering the full v3 surface |

## Files

```
scalar-api-docs/
    index.html            # Landing page
    v3beta.html           # Scalar reference for v3beta Public API
    v3.html               # Scalar reference for v3 Platform API
    extract_specs.py      # Extracts v3beta and v3 subsets from full spec
    serve.sh              # Downloads spec, extracts, serves locally
    .gitignore            # Excludes specs/ (generated)
    specs/                # Generated at runtime (not committed)
        openapi-source.yaml
        openapi-v3beta.yaml
        openapi-v3.yaml
```

## How it works

1. `serve.sh` downloads the OpenAPI 3.0.3 spec from `calculi-corp/api` via the GitHub CLI (or copies a local file if `-f` is used)
2. `extract_specs.py` parses the full spec (500+ endpoints) and extracts two subsets:
   - `/v3beta/*` paths and their schema dependencies (Public API)
   - `/v3/*` paths and their schema dependencies (Platform API)
3. Scalar renders the specs client-side from a CDN (no build step, no npm)
4. Python's built-in HTTP server serves the static files locally
