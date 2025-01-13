#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Trisha's favorite accounting jokes
JOKES=(
    "Why did the accountant cross the road? To get to the other side... of the balance sheet! 📊"
    "What's an accountant's favorite time? FISCAL time! ⏰"
    "How does Trisha organize her AI thoughts? Double-entry bookkeeping! 🤖"
    "What's Trisha's favorite movie? The Accountant... but with more jokes! 🎬"
)

# Print a random Trisha joke
trisha_says() {
    RANDOM_JOKE=${JOKES[$RANDOM % ${#JOKES[@]}]}
    echo -e "${PURPLE}Tri says: $RANDOM_JOKE${NC}"
}

# Check for required tools
check_requirements() {
    local missing=0
    command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3 is required but not installed.${NC}"; missing=1; }
    command -v poetry >/dev/null 2>&1 || { echo -e "${RED}❌ Poetry is required but not installed.${NC}"; missing=1; }
    command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required but not installed.${NC}"; missing=1; }
    command -v node >/dev/null 2>&1 || { echo -e "${RED}❌ Node.js is required but not installed.${NC}"; missing=1; }
    command -v pnpm >/dev/null 2>&1 || { echo -e "${RED}❌ pnpm is required but not installed.${NC}"; missing=1; }
    
    if [ $missing -eq 1 ]; then
        echo -e "${RED}Please install missing requirements and try again!${NC}"
        exit 1
    fi
}

# Service management
start_services() {
    echo -e "${BLUE}Starting all services...${NC}"
    
    # Start Qdrant
    if ! docker ps | grep -q qdrant; then
        echo -e "${YELLOW}Starting Qdrant...${NC}"
        docker run -d -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
    fi
    
    # Start SSH server
    echo -e "${YELLOW}Starting SSH server...${NC}"
    poetry run python -m packages.mcp-server-enhanced-ssh &
    
    # Start API server
    echo -e "${YELLOW}Starting API server...${NC}"
    poetry run python -m packages.mcp-atc.src.api.main &
    
    echo -e "${GREEN}All services started! 🚀${NC}"
    trisha_says
}

stop_services() {
    echo -e "${BLUE}Stopping all services...${NC}"
    
    # Stop Docker containers
    docker stop $(docker ps -q --filter ancestor=qdrant/qdrant) 2>/dev/null
    
    # Stop Python processes
    pkill -f "python -m packages.mcp-server-enhanced-ssh"
    pkill -f "python -m packages.mcp-atc.src.api.main"
    
    echo -e "${GREEN}All services stopped! 🛑${NC}"
    trisha_says
}

status_services() {
    echo -e "${BLUE}Checking services status...${NC}"
    
    # Check Qdrant
    if docker ps | grep -q qdrant; then
        echo -e "${GREEN}✅ Qdrant is running${NC}"
    else
        echo -e "${RED}❌ Qdrant is not running${NC}"
    fi
    
    # Check SSH server
    if pgrep -f "python -m packages.mcp-server-enhanced-ssh" > /dev/null; then
        echo -e "${GREEN}✅ SSH server is running${NC}"
    else
        echo -e "${RED}❌ SSH server is not running${NC}"
    fi
    
    # Check API server
    if pgrep -f "python -m packages.mcp-atc.src.api.main" > /dev/null; then
        echo -e "${GREEN}✅ API server is running${NC}"
    else
        echo -e "${RED}❌ API server is not running${NC}"
    fi
    
    trisha_says
}

# Testing and coverage
run_tests() {
    echo -e "${BLUE}Running tests...${NC}"
    poetry run pytest
    trisha_says
}

check_coverage() {
    echo -e "${BLUE}Running tests with coverage...${NC}"
    poetry run pytest --cov=src --cov-report=term-missing
    trisha_says
}

# Code formatting
format_code() {
    echo -e "${BLUE}Formatting code...${NC}"
    poetry run black .
    poetry run isort .
    echo -e "${GREEN}Code formatted! ✨${NC}"
    trisha_says
}

# System check
doctor() {
    echo -e "${BLUE}Running system check...${NC}"
    check_requirements
    
    # Check Python environment
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✅ Python virtual environment exists${NC}"
    else
        echo -e "${RED}❌ Python virtual environment missing${NC}"
    fi
    
    # Check Node modules
    if [ -d "node_modules" ]; then
        echo -e "${GREEN}✅ Node modules installed${NC}"
    else
        echo -e "${RED}❌ Node modules missing${NC}"
    fi
    
    # Check ports
    if ! lsof -i:6333 >/dev/null; then
        echo -e "${GREEN}✅ Port 6333 available for Qdrant${NC}"
    else
        echo -e "${RED}❌ Port 6333 in use${NC}"
    fi
    
    if ! lsof -i:2222 >/dev/null; then
        echo -e "${GREEN}✅ Port 2222 available for SSH${NC}"
    else
        echo -e "${RED}❌ Port 2222 in use${NC}"
    fi
    
    if ! lsof -i:8000 >/dev/null; then
        echo -e "${GREEN}✅ Port 8000 available for API${NC}"
    else
        echo -e "${RED}❌ Port 8000 in use${NC}"
    fi
    
    trisha_says
}

# Clean up
clean() {
    echo -e "${BLUE}Cleaning up...${NC}"
    rm -rf .venv
    rm -rf node_modules
    rm -rf __pycache__
    rm -rf .pytest_cache
    rm -rf .coverage
    echo -e "${GREEN}All clean! 🧹${NC}"
    trisha_says
}

# Command line interface
case "${1:-menu}" in
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        ;;
    "status")
        status_services
        ;;
    "test")
        run_tests
        ;;
    "test-coverage")
        check_coverage
        ;;
    "format")
        format_code
        ;;
    "doctor")
        doctor
        ;;
    "clean")
        clean
        ;;
    "menu")
        # Main menu
        while true; do
            echo -e "\n${PURPLE}=== MCP Management System ===${NC}"
            echo -e "${BLUE}1) Start all services${NC}"
            echo -e "${BLUE}2) Stop all services${NC}"
            echo -e "${BLUE}3) Check services status${NC}"
            echo -e "${BLUE}4) Run tests${NC}"
            echo -e "${BLUE}5) Check coverage${NC}"
            echo -e "${BLUE}6) Format code${NC}"
            echo -e "${BLUE}7) Run system check${NC}"
            echo -e "${BLUE}8) Clean up${NC}"
            echo -e "${BLUE}9) Exit${NC}"
            
            read -p "Enter your choice: " choice
            
            case $choice in
                1) start_services ;;
                2) stop_services ;;
                3) status_services ;;
                4) run_tests ;;
                5) check_coverage ;;
                6) format_code ;;
                7) doctor ;;
                8) clean ;;
                9)
                    echo -e "${PURPLE}Tri says: Time to balance those books! See you next time! 👋${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${PURPLE}Tri says: That's not a valid option! Like trying to debit a credit! Try again. 😅${NC}"
                    ;;
            esac
        done
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Usage: $0 {start|stop|restart|status|test|test-coverage|format|doctor|clean|menu}"
        exit 1
        ;;
esac 