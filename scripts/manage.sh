#!/bin/bash

# ===========================================
# MCP Management System - Enhanced Edition
# ===========================================
# Aye and Hue's masterpiece of system control
# With Trisha's seal of approval! 🤖📊
# ===========================================

# Color Definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set absolute paths first
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SSH_SERVER_DIR="$ROOT_DIR/packages/mcp-server-enhanced-ssh"
ATC_DIR="$ROOT_DIR/packages/mcp-atc"

# Configuration Section
# ---------------------
QD_IMAGE="qdrant/qdrant"
QD_PORT=6333
SSH_PORT=2222
API_PORT=8000
LOG_DIR="$ROOT_DIR/logs"
CONFIG_DIR="$ROOT_DIR/config"
BACKUP_DIR="$ROOT_DIR/backups"

# Ensure essential directories exist before any logging happens
mkdir -p "$LOG_DIR" "$CONFIG_DIR" "$BACKUP_DIR"

# Verify directories exist
if [ ! -d "$SSH_SERVER_DIR" ]; then
    log "ERROR" "SSH server directory not found: $SSH_SERVER_DIR"
    exit 1
fi

if [ ! -d "$ATC_DIR" ]; then
    log "ERROR" "ATC directory not found: $ATC_DIR"
    exit 1
fi

# Trisha's Accounting Jokes
JOKES=(
    "Why did the accountant cross the road? To get to the other side... of the balance sheet! 📊"
    "What's an accountant's favorite time? FISCAL time! ⏰"
    "How does Trisha organize her AI thoughts? Double-entry bookkeeping! 🤖"
    "What's Trisha's favorite movie? The Accountant... but with more jokes! 🎬"
    "What's an AI's favorite financial statement? The cash FLOW chart! 💸"
)

# Enhanced Logging Function
log() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local log_file="$LOG_DIR/mcp_$(date +"%Y%m%d").log"
    
    case $level in
        INFO) color=$BLUE ;;
        WARN) color=$YELLOW ;;
        ERROR) color=$RED ;;
        SUCCESS) color=$GREEN ;;
        *) color=$NC ;;
    esac
    
    echo -e "${color}[$timestamp] [$level] $message${NC}"
    echo "[$timestamp] [$level] $message" >> $log_file
}

# Print a random Trisha joke
trisha_says() {
    RANDOM_JOKE=${JOKES[$RANDOM % ${#JOKES[@]}]}
    echo -e "${PURPLE}Tri says: $RANDOM_JOKE${NC}"
}

# Check for required tools, ports, and services
check_requirements() {
    local missing=0
    command -v python3 >/dev/null 2>&1 || { log "ERROR" "Python 3 is required but not installed"; missing=1; }
    command -v poetry >/dev/null 2>&1 || { log "ERROR" "Poetry is required but not installed"; missing=1; }
    command -v node >/dev/null 2>&1 || { log "ERROR" "Node.js is required but not installed"; missing=1; }
    command -v pnpm >/dev/null 2>&1 || { log "ERROR" "pnpm is required but not installed"; missing=1; }
    command -v lsof >/dev/null 2>&1 || { log "ERROR" "lsof is required but not installed"; missing=1; }

    if [ $missing -eq 1 ]; then
        log "ERROR" "Please install missing requirements and try again!"
        exit 1
    fi

    # Check if Docker is available (optional)
    if ! command -v docker >/dev/null 2>&1; then
        log "WARN" "Docker not found - will use external Qdrant if available"
    else
        # Check if Docker daemon is running (optional)
        docker info >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            log "WARN" "Docker daemon not running - will use external Qdrant if available"
        fi
    fi
}

# Check if a port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Kill process using a port
kill_port() {
    local port=$1
    local pid=$(lsof -t -i :$port)
    if [ ! -z "$pid" ]; then
        log "INFO" "Killing process using port $port (PID: $pid)"
        kill -9 $pid 2>/dev/null
        sleep 1
    fi
}

# Cleanup ports before starting services
cleanup_ports() {
    local ports=($QD_PORT $SSH_PORT $API_PORT)
    for port in "${ports[@]}"; do
        if check_port $port; then
            kill_port $port
        fi
    done
}

# Service Management Functions
# ----------------------------

start_services() {
    log "INFO" "Starting all services..."
    
    # Clean up any stale ports first
    cleanup_ports
    
    # Start Qdrant
    start_qdrant
    # Start API server first since SSH server depends on it
    log "INFO" "Starting API server..."
    cd "$ATC_DIR"
    
    # Install dependencies if needed
    if [ ! -d ".venv" ]; then
        log "INFO" "Installing Python dependencies..."
        poetry install
        if [ $? -ne 0 ]; then
            log "ERROR" "Failed to install Python dependencies"
            cd "$ROOT_DIR"
            return 1
        fi
    fi
    
    # Start the API server using poetry
    PYTHONPATH="$ATC_DIR/src" poetry run uvicorn mcp_atc.api.main:app --host 0.0.0.0 --port $API_PORT &
    API_PID=$!
    sleep 3  # Give the server a moment to start
    
    if ps -p $API_PID > /dev/null; then
        log "SUCCESS" "API server started successfully!"
    else
        log "ERROR" "Failed to start API server"
        cd "$ROOT_DIR"
        return 1
    fi
    cd "$ROOT_DIR"
    cd "$ROOT_DIR"
    
    # Start SSH server
    log "INFO" "Starting SSH server..."
    cd "$SSH_SERVER_DIR"
    
    # Ensure dependencies are installed and built
    if [ ! -d "node_modules" ] || [ ! -f "dist/index.js" ]; then
        log "INFO" "Installing and building SSH server..."
        pnpm install && pnpm build
        if [ $? -ne 0 ]; then
            log "ERROR" "Failed to build SSH server"
            cd "$ROOT_DIR"
            return 1
        fi
    fi
    
    # Start the server
    NODE_ENV=production node dist/index.js &
    SSH_PID=$!
    sleep 3  # Give the server more time to start and connect to API
    
    if ps -p $SSH_PID > /dev/null; then
        log "SUCCESS" "SSH server started successfully!"
    else
        log "ERROR" "Failed to start SSH server"
        cd "$ROOT_DIR"
        return 1
    fi
    cd "$ROOT_DIR"
    
    log "SUCCESS" "All services started! 🚀"
    trisha_says
}

stop_services() {
    log "INFO" "Stopping all services..."
    
    # Stop Qdrant
    stop_qdrant
    
    # Stop Python processes
    log "INFO" "Stopping Python servers..."
    
    # Find and stop SSH server
    SSH_PID=$(pgrep -f "node.*$SSH_SERVER_DIR/dist/index.js")
    if [ ! -z "$SSH_PID" ]; then
        log "INFO" "Stopping SSH server (PID: $SSH_PID)..."
        kill $SSH_PID 2>/dev/null
        
        # Wait for process to stop gracefully
        for i in {1..5}; do
            if ! ps -p $SSH_PID > /dev/null 2>&1; then
                log "SUCCESS" "SSH server stopped gracefully"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p $SSH_PID > /dev/null 2>&1; then
            log "WARN" "SSH server not responding, forcing shutdown..."
            kill -9 $SSH_PID 2>/dev/null
            if [ $? -eq 0 ]; then
                log "SUCCESS" "SSH server terminated"
            else
                log "ERROR" "Failed to terminate SSH server"
                return 1
            fi
        fi
    else
        log "INFO" "SSH server was not running"
    fi
    
    # Find and stop API server
    API_PID=$(pgrep -f "uvicorn.*mcp_atc.api.main:app")
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        # Wait for process to stop
        for i in {1..5}; do
            if ! ps -p $API_PID > /dev/null 2>&1; then
                log "SUCCESS" "API server stopped"
                break
            fi
            sleep 1
        done
        if ps -p $API_PID > /dev/null 2>&1; then
            log "ERROR" "Failed to stop API server gracefully, forcing..."
            kill -9 $API_PID 2>/dev/null
        fi
    else
        log "INFO" "API server was not running"
    fi
    
    # Final verification
    sleep 1
    if ! pgrep -f "node.*$SSH_SERVER_DIR/dist/index.js" > /dev/null && \
       ! pgrep -f "uvicorn.*mcp_atc.api.main:app" > /dev/null; then
        log "SUCCESS" "All services stopped! 🛑"
    else
        log "ERROR" "Some services failed to stop"
        return 1
    fi
    
    trisha_says
}

start_qdrant() {
    # First check if something is already running on Qdrant port
    if check_port $QD_PORT; then
        log "INFO" "Port $QD_PORT is already in use, assuming Qdrant is running externally"
        return 0
    fi

    # Verify Docker is running first
    docker info >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        log "ERROR" "Cannot start Qdrant: Docker daemon is not running"
        return 1
    fi

    # Check if container already exists
    if docker ps -a | grep -q qdrant; then
        log "INFO" "Removing existing Qdrant container..."
        docker rm -f qdrant >/dev/null 2>&1
    fi

    # Start new container
    log "INFO" "Starting Qdrant vector database..."
    if docker run -d -p $QD_PORT:6333 --name qdrant $QD_IMAGE >/dev/null 2>&1; then
        # Wait for container to be healthy
        for i in {1..10}; do
            if docker ps | grep -q qdrant; then
                log "SUCCESS" "Qdrant started successfully!"
                return 0
            fi
            sleep 1
        done
        log "ERROR" "Qdrant container failed to start properly"
        return 1
    else
        log "ERROR" "Failed to start Qdrant container"
        return 1
    fi
}

stop_qdrant() {
    # Check if port is in use
    if ! check_port $QD_PORT; then
        log "INFO" "No service found on Qdrant port $QD_PORT"
        return 0
    fi

    # Verify Docker is running first
    docker info >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        log "WARN" "Cannot check Docker Qdrant status: Docker daemon is not running"
        log "INFO" "Assuming external Qdrant instance, skipping stop"
        return 0
    fi

    # Check if container exists and stop it
    if docker ps | grep -q qdrant; then
        log "INFO" "Stopping Docker-managed Qdrant..."
        if docker stop qdrant >/dev/null 2>&1; then
            log "INFO" "Removing Qdrant container..."
            if docker rm qdrant >/dev/null 2>&1; then
                log "SUCCESS" "Docker-managed Qdrant stopped and removed successfully!"
            else
                log "ERROR" "Failed to remove Qdrant container"
                return 1
            fi
        else
            log "ERROR" "Failed to stop Qdrant"
            return 1
        fi
    else
        log "INFO" "Found Qdrant on port $QD_PORT but not managed by Docker, leaving it running"
    fi
}

status_services() {
    log "INFO" "Checking services status..."
    
    # Check Qdrant
    if check_port $QD_PORT; then
        # Check if it's Docker-managed
        if docker info >/dev/null 2>&1 && docker ps 2>/dev/null | grep -q qdrant; then
            log "SUCCESS" "✅ Docker-managed Qdrant is running"
        else
            log "SUCCESS" "✅ External Qdrant instance detected on port $QD_PORT"
        fi
    else
        log "WARN" "❌ No Qdrant instance found"
    fi
    
    # Check SSH server
    if pgrep -f "node.*$SSH_SERVER_DIR/dist/index.js" > /dev/null; then
        log "SUCCESS" "✅ SSH server is running"
    else
        log "WARN" "❌ SSH server is not running"
    fi
    
    # Check API server
    if pgrep -f "uvicorn.*mcp_atc.api.main:app" > /dev/null; then
        log "SUCCESS" "✅ API server is running"
    else
        log "WARN" "❌ API server is not running"
    fi
    
    trisha_says
}

view_logs() {
    if [ -d "$LOG_DIR" ]; then
        local log_file="$LOG_DIR/mcp_$(date +"%Y%m%d").log"
        if [ -f "$log_file" ]; then
            less "$log_file"
        else
            log "WARN" "No logs found for today"
        fi
    else
        log "ERROR" "Log directory not found"
    fi
}

# Testing and coverage
run_tests() {
    log "INFO" "Running tests..."
    poetry run pytest
    if [ $? -eq 0 ]; then
        log "SUCCESS" "All tests passed! 🎉"
    else
        log "ERROR" "Some tests failed! 😢"
    fi
    trisha_says
}

check_coverage() {
    log "INFO" "Running tests with coverage..."
    poetry run pytest --cov=src --cov-report=term-missing
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Coverage report generated! 📊"
    else
        log "ERROR" "Failed to generate coverage report"
    fi
    trisha_says
}

# Code formatting
format_code() {
    log "INFO" "Formatting Python code..."
    poetry run black .
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Python code formatted with black"
    else
        log "ERROR" "Failed to format Python code"
    fi
    
    log "INFO" "Sorting imports..."
    poetry run isort .
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Imports sorted successfully"
    else
        log "ERROR" "Failed to sort imports"
    fi
    
    log "INFO" "Formatting TypeScript code..."
    pnpm prettier --write "packages/**/*.ts"
    if [ $? -eq 0 ]; then
        log "SUCCESS" "TypeScript code formatted with prettier"
    else
        log "ERROR" "Failed to format TypeScript code"
    fi
    
    log "SUCCESS" "All code formatted! ✨"
    trisha_says
}

# Clean up
clean() {
    log "INFO" "Cleaning up project..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    
    # Remove coverage files
    rm -f .coverage
    rm -rf htmlcov/
    
    # Remove logs
    rm -rf $LOG_DIR/*
    
    # Remove Node modules
    rm -rf node_modules/
    find . -name "node_modules" -type d -prune -exec rm -rf {} +
    
    # Remove virtual environments
    rm -rf .venv/
    
    log "SUCCESS" "Project cleaned up! 🧹"
    trisha_says
}

# Test voices
test_voices() {
    log "INFO" "Testing AI voices..."
    poetry run python -c "
import asyncio
from src.core.voice import test_voices
asyncio.run(test_voices())
"
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Voice test completed! 🎤"
    else
        log "ERROR" "Voice test failed"
    fi
    trisha_says
}

# Backup configuration
backup_config() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$BACKUP_DIR/mcp_config_$timestamp.tar.gz"
    
    log "INFO" "Creating configuration backup..."
    
    # Create list of files to backup
    local files_to_backup=(
        "pyproject.toml"
        "poetry.lock"
        "package.json"
        "pnpm-lock.yaml"
        ".env"
        "config/"
    )
    
    # Check if files exist before backing up
    local existing_files=()
    for file in "${files_to_backup[@]}"; do
        if [ -e "$file" ]; then
            existing_files+=("$file")
        fi
    done
    
    if [ ${#existing_files[@]} -eq 0 ]; then
        log "ERROR" "No configuration files found to backup"
        return 1
    fi
    
    # Create backup
    tar -czf "$backup_file" "${existing_files[@]}" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Configuration backed up to: $backup_file 💾"
        
        # List backup contents
        log "INFO" "Backup contains:"
        tar -tzf "$backup_file" | while read -r line; do
            log "INFO" "  - $line"
        done
    else
        log "ERROR" "Failed to create backup"
        return 1
    fi
    
    trisha_says
}

# Main Menu
show_menu() {
    clear
    echo -e "\n${PURPLE}=== MCP Management System ===${NC}"
    echo -e "${BLUE}1) Start all services${NC}"
    echo -e "${BLUE}2) Stop all services${NC}"
    echo -e "${BLUE}3) Restart all services${NC}"
    echo -e "${BLUE}4) Check service status${NC}"
    echo -e "${BLUE}5) Run tests${NC}"
    echo -e "${BLUE}6) Check test coverage${NC}"
    echo -e "${BLUE}7) Format code${NC}"
    echo -e "${BLUE}8) Run system check${NC}"
    echo -e "${BLUE}9) Clean up${NC}"
    echo -e "${BLUE}10) Test voices${NC}"
    echo -e "${BLUE}11) View Logs${NC}"
    echo -e "${BLUE}12) Backup Configuration${NC}"
    echo -e "${BLUE}13) Exit${NC}"
}

# Main Execution
case $1 in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services && start_services
        ;;
    status)
        status_services
        ;;
    menu)
        while true; do
            show_menu
            trisha_says
            read -p "Enter your choice: " choice

            case $choice in
                1) start_services ;;
                2) stop_services ;;
                3) stop_services && start_services ;;
                4) status_services ;;
                5) run_tests ;;
                6) check_coverage ;;
                7) format_code ;;
                8) check_requirements ;;
                9) clean ;;
                10) test_voices ;;
                11) view_logs ;;
                12) backup_config ;;
                13)
                    echo -e "${PURPLE}Tri says: Time to balance those books! See you next time! 👋${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${PURPLE}Tri says: That's not a valid option! Like trying to debit a credit! Try again. 😅${NC}"
                    ;;
            esac
            
            # Add a small pause to read the output
            sleep 2
        done
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Usage: $0 {start|stop|restart|status|menu}"
        exit 1
        ;;
esac