#!/bin/bash

# 🌈 Colors make life better! 🌈
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ASCII Art because why not? 🎨
print_banner() {
    echo -e "${MAGENTA}"
    echo "  _____ _____ _    _ _____   _____ _____ _____ _    _ "
    echo " |_   _|  _  | |  | |  ___| /  ___|  ___|  _  | |  | |"
    echo "   | | | | | | |  | | |__   \ `--.| |__ | | | | |__| |"
    echo "   | | | | | | |/\| |  __|   `--. \  __|| | | |  __  |"
    echo "   | | \ \_/ /  /\  / |___  /\__/ / |___\ \_/ / |  | |"
    echo "   \_/  \___/\/  \/\____/  \____/\____/ \___/\_|  |_/"
    echo -e "${NC}"
    echo -e "${CYAN}🚀 Enhanced SSH Server with Tmux Magic! ✨${NC}\n"
}

# Fun loading animation 🌀
show_spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Check if tmux is installed 🔍
check_tmux() {
    if ! command -v tmux &> /dev/null; then
        echo -e "${RED}🚫 Tmux is not installed! Let's fix that...${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install tmux
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y tmux
        else
            echo -e "${RED}❌ Unsupported OS for automatic tmux installation${NC}"
            exit 1
        fi
    fi
}

# Check if required directories exist 📁
setup_directories() {
    local dirs=(
        "$HOME/.tmux-sockets"
        "$HOME/.tmux/resurrect"
        "$HOME/.ssh/enhanced-ssh"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            echo -e "${YELLOW}📁 Creating directory: $dir${NC}"
            mkdir -p "$dir"
        fi
    done
}

# Start the enhanced SSH server 🚀
start_server() {
    echo -e "${GREEN}🚀 Starting Enhanced SSH Server...${NC}"
    check_tmux
    setup_directories
    
    cd "$(dirname "$0")/../packages/mcp-server-enhanced-ssh"
    
    # Build if needed
    if [ ! -d "dist" ]; then
        echo -e "${YELLOW}🔨 Building server...${NC}"
        npm run build
    fi
    
    # Start server in tmux session
    SESSION_NAME="enhanced-ssh"
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Server is already running!${NC}"
        echo -e "Use ${CYAN}$0 attach${NC} to connect to it"
        return
    fi
    
    tmux new-session -d -s "$SESSION_NAME" "npm run start"
    echo -e "${GREEN}✅ Server started in tmux session: $SESSION_NAME${NC}"
    echo -e "Use ${CYAN}$0 attach${NC} to connect to the server session"
}

# Stop the server 🛑
stop_server() {
    echo -e "${YELLOW}🛑 Stopping Enhanced SSH Server...${NC}"
    SESSION_NAME="enhanced-ssh"
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        tmux kill-session -t "$SESSION_NAME"
        echo -e "${GREEN}✅ Server stopped successfully${NC}"
    else
        echo -e "${RED}❌ Server is not running${NC}"
    fi
}

# Attach to the server session 🔌
attach_server() {
    SESSION_NAME="enhanced-ssh"
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${GREEN}🔌 Attaching to server session...${NC}"
        tmux attach-session -t "$SESSION_NAME"
    else
        echo -e "${RED}❌ Server is not running${NC}"
        echo -e "Start it with: ${CYAN}$0 start${NC}"
    fi
}

# Show server status 📊
show_status() {
    SESSION_NAME="enhanced-ssh"
    echo -e "${CYAN}📊 Server Status${NC}"
    echo -e "${BOLD}-------------------${NC}"
    
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo -e "${GREEN}✅ Server is running${NC}"
        echo -e "${BOLD}Active sessions:${NC}"
        tmux list-clients -t "$SESSION_NAME" 2>/dev/null || echo "No active clients"
    else
        echo -e "${RED}❌ Server is not running${NC}"
    fi
    
    echo -e "\n${BOLD}Socket directory:${NC}"
    ls -l "$HOME/.tmux-sockets" 2>/dev/null || echo "No sockets found"
}

# Show help message 📖
show_help() {
    print_banner
    echo -e "${BOLD}Usage:${NC} $0 [command]"
    echo
    echo -e "${BOLD}Commands:${NC}"
    echo -e "  ${CYAN}start${NC}    - Start the enhanced SSH server"
    echo -e "  ${CYAN}stop${NC}     - Stop the server"
    echo -e "  ${CYAN}restart${NC}  - Restart the server"
    echo -e "  ${CYAN}attach${NC}   - Attach to the server tmux session"
    echo -e "  ${CYAN}status${NC}   - Show server status"
    echo -e "  ${CYAN}help${NC}     - Show this help message"
    echo
    echo -e "${YELLOW}Pro Tip:${NC} Use ${CYAN}Ctrl+b d${NC} to detach from the server session!"
}

# Main command handler 🎮
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    attach)
        attach_server
        ;;
    status)
        show_status
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo -e "Use ${CYAN}$0 help${NC} to see available commands"
        exit 1
        ;;
esac

exit 0