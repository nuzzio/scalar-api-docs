#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SPECS_DIR="$SCRIPT_DIR/specs"
REPO="calculi-corp/api"
SPEC_PATH="openapiV3/openapi.yaml"
PORT="8787"

usage() {
    echo "Usage: ./serve.sh [options]"
    echo ""
    echo "Options:"
    echo "  -b, --branch BRANCH   Git branch to download from (default: main)"
    echo "  -f, --file PATH       Use a local OpenAPI spec file instead of downloading"
    echo "  -p, --port PORT       Port to serve on (default: 8787)"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Examples:"
    echo "  ./serve.sh                          # Download from main, serve on 8787"
    echo "  ./serve.sh -b develop               # Download from develop branch"
    echo "  ./serve.sh -f /path/to/openapi.yaml # Use a local file"
    echo "  ./serve.sh -b develop -p 9090       # Custom branch and port"
}

BRANCH="main"
LOCAL_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--branch) BRANCH="$2"; shift 2 ;;
        -f|--file)   LOCAL_FILE="$2"; shift 2 ;;
        -p|--port)   PORT="$2"; shift 2 ;;
        -h|--help)   usage; exit 0 ;;
        *)           echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

mkdir -p "$SPECS_DIR"

echo "=== CloudBees API Docs (Scalar) ==="
echo ""

if [[ -n "$LOCAL_FILE" ]]; then
    # Use local file
    if [[ ! -f "$LOCAL_FILE" ]]; then
        echo "Error: File not found: $LOCAL_FILE"
        exit 1
    fi
    echo "  Source: $LOCAL_FILE (local file)"
    cp "$LOCAL_FILE" "$SPECS_DIR/openapi-source.yaml"
    echo "  Copied to specs/openapi-source.yaml"
else
    # Download from GitHub
    echo "  Source: $REPO @ $BRANCH"
    echo "  Spec:   $SPEC_PATH"
    echo ""
    echo "Downloading OpenAPI spec..."
    if command -v gh &> /dev/null; then
        gh api "repos/$REPO/contents/$SPEC_PATH?ref=$BRANCH" \
            -H "Accept: application/vnd.github.raw+type" \
            > "$SPECS_DIR/openapi-source.yaml"
    else
        echo "Error: GitHub CLI (gh) is required to download from GitHub."
        echo ""
        echo "  Install:  brew install gh"
        echo "  Auth:     gh auth login"
        echo ""
        echo "Or use a local file instead:"
        echo "  ./serve.sh -f /path/to/openapi.yaml"
        exit 1
    fi
    echo "  Downloaded: specs/openapi-source.yaml"
fi

# Check for pyyaml
if ! python3 -c "import yaml" 2>/dev/null; then
    echo ""
    echo "Installing pyyaml..."
    pip3 install pyyaml --quiet
fi

# Extract v3beta and v3 specs
echo ""
cd "$SCRIPT_DIR"
python3 extract_specs.py

# Serve
echo ""
echo "=== Starting server on http://localhost:$PORT ==="
echo ""
echo "  Landing page:  http://localhost:$PORT"
echo "  v3beta API:    http://localhost:$PORT/v3beta.html"
echo "  v3 API:        http://localhost:$PORT/v3.html"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

python3 -m http.server "$PORT"
