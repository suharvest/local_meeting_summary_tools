#!/bin/bash
# Development startup script - builds frontend and starts server on single port

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "  Meeting Assistant - Development Server"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if config.yaml exists
if [ ! -f "config.yaml" ]; then
    echo -e "${RED}Error: config.yaml not found!${NC}"
    echo "Please copy config.example.yaml to config.yaml and fill in your credentials."
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend && npm install && cd ..
fi

# Build frontend
echo ""
echo -e "${YELLOW}Building frontend...${NC}"
cd frontend && npm run build && cd ..
echo -e "${GREEN}Frontend built successfully!${NC}"

# Start server
echo ""
echo "=========================================="
echo -e "${GREEN}Starting server on port 5173...${NC}"
echo ""
echo "  Open: http://localhost:5173"
echo "  API Docs: http://localhost:5173/docs"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="

uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 5173
