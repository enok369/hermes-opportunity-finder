#!/bin/bash
# Hermes Opportunity Finder - Startup & Management Script
# Usage: ./hermes-setup.sh [init|start|stop|logs|status|reset]

set -euo pipefail

# Configuration
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
OPPORTUNITIES_DIR="${OPPORTUNITIES_DIR:-$HOME/opportunities}"
COMPOSE_FILE="docker-compose.yml"
LOG_FILE="${HERMES_HOME}/logs/setup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local msg="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${msg}" | tee -a "${LOG_FILE}"
}

# Info/success/warn functions
info() { echo -e "${BLUE}ℹ${NC} $@"; log "INFO" "$@"; }
success() { echo -e "${GREEN}✓${NC} $@"; log "SUCCESS" "$@"; }
warn() { echo -e "${YELLOW}⚠${NC} $@"; log "WARN" "$@"; }
error() { echo -e "${RED}✗${NC} $@"; log "ERROR" "$@"; }

# Ensure directories exist
init_directories() {
    info "Initializing directory structure..."
    
    mkdir -p "${HERMES_HOME}"/{config,skills,memory,logs,plugins,sessions}
    mkdir -p "${OPPORTUNITIES_DIR}"/{proposals,feedback,archive,reports}
    
    success "Directories created"
}

# Install Hermes locally if not present
install_hermes() {
    if command -v hermes &> /dev/null; then
        success "Hermes already installed: $(hermes --version)"
        return 0
    fi
    
    info "Installing Hermes Agent..."
    curl -fsSL https://install.hermes.nousresearch.com | bash
    
    success "Hermes installed"
}

# Setup configuration files
setup_config() {
    info "Setting up Hermes configuration..."
    
    # Copy config to Hermes home
    if [ -f "hermes-config.yaml" ]; then
        cp hermes-config.yaml "${HERMES_HOME}/config.yaml"
        success "Config copied"
    else
        warn "hermes-config.yaml not found - using defaults"
    fi
    
    # Copy skills to Hermes skills directory
    if [ -d "hermes-skills" ]; then
        mkdir -p "${HERMES_HOME}/skills"
        cp hermes-skills/*.py "${HERMES_HOME}/skills/" || true
        success "Skills copied"
    else
        warn "hermes-skills directory not found"
    fi
    
    # Copy cron config
    if [ -f "hermes-crontab.yaml" ]; then
        cp hermes-crontab.yaml "${HERMES_HOME}/crontab.yaml"
        success "Cron tasks copied"
    else
        warn "hermes-crontab.yaml not found"
    fi
}

# Check Docker and GPU
check_prerequisites() {
    info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install Docker Desktop."
        exit 1
    fi
    
    if ! docker ps &> /dev/null; then
        error "Docker daemon not running or not accessible"
        exit 1
    fi
    
    success "Docker is running"
    
    # Check for GPU
    if command -v nvidia-smi &> /dev/null; then
        info "NVIDIA GPU detected:"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | sed 's/^/  /'
    else
        warn "NVIDIA GPU not detected - Model Runner will use CPU (slower)"
    fi
}

# Initialize Hermes profile and backend
init_hermes() {
    info "Initializing Hermes backend..."
    
    # Ensure Hermes home is set up
    export HERMES_HOME="${HERMES_HOME}"
    
    # Create default profile if needed
    if [ ! -d "${HERMES_HOME}/profiles" ]; then
        info "Creating Hermes profiles directory"
        mkdir -p "${HERMES_HOME}/profiles/default"
    fi
    
    success "Hermes initialized"
}

# Start Docker Compose stack
start_docker_stack() {
    info "Starting Docker services (Model Runner + Hermes backend)..."
    
    if [ ! -f "${COMPOSE_FILE}" ]; then
        error "docker-compose.yml not found"
        exit 1
    fi
    
    docker compose up -d
    
    info "Waiting for services to be healthy..."
    sleep 10
    
    # Check health
    if docker compose exec -T model-runner curl -s http://localhost:8000/health &> /dev/null; then
        success "Model Runner is ready"
    else
        error "Model Runner failed to start"
        docker compose logs model-runner
        exit 1
    fi
    
    if docker compose exec -T hermes-backend curl -s http://localhost:9119/api/status &> /dev/null; then
        success "Hermes backend is ready"
    else
        error "Hermes backend failed to start"
        docker compose logs hermes-backend
        exit 1
    fi
    
    success "All services started successfully"
}

# Display access information
show_access_info() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}   Hermes Opportunity Finder is Running!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "📍 Hermes Backend:    http://localhost:9119"
    echo "🤖 Model Runner:      http://localhost:8000"
    echo "📁 Hermes Home:       ${HERMES_HOME}"
    echo "📋 Opportunities:     ${OPPORTUNITIES_DIR}"
    echo ""
    echo "🖥️  Launch Desktop App:"
    echo "   hermes desktop"
    echo ""
    echo "📊 View Web Dashboard:"
    echo "   hermes dashboard"
    echo ""
    echo "⚙️  Configure Hermes:"
    echo "   export HERMES_HOME=${HERMES_HOME}"
    echo "   hermes config"
    echo ""
    echo "📜 View Logs:"
    echo "   docker compose logs -f"
    echo "   tail -f ${LOG_FILE}"
    echo ""
    echo "🛑 Stop Services:"
    echo "   docker compose down"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

# Stop Docker stack
stop_docker_stack() {
    info "Stopping Docker services..."
    docker compose down
    success "Services stopped"
}

# Show status
show_status() {
    info "Service Status:"
    echo ""
    docker compose ps
    echo ""
}

# Show logs
show_logs() {
    info "Following Docker Compose logs (Ctrl+C to exit)..."
    docker compose logs -f
}

# Reset everything
reset_all() {
    warn "This will reset all Hermes data and stop containers"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Reset cancelled"
        return 0
    fi
    
    info "Stopping containers..."
    docker compose down -v
    
    info "Removing Hermes data..."
    rm -rf "${HERMES_HOME}"
    
    success "Reset complete"
}

# Main command dispatch
main() {
    local cmd="${1:-start}"
    
    # Ensure log directory exists
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    case "${cmd}" in
        init)
            info "Initializing Hermes Opportunity Finder setup..."
            check_prerequisites
            init_directories
            install_hermes
            setup_config
            init_hermes
            success "Initialization complete!"
            ;;
        
        start)
            info "Starting Hermes Opportunity Finder..."
            check_prerequisites
            init_directories
            start_docker_stack
            show_access_info
            ;;
        
        stop)
            stop_docker_stack
            ;;
        
        restart)
            info "Restarting services..."
            stop_docker_stack
            sleep 2
            start_docker_stack
            show_access_info
            ;;
        
        status)
            show_status
            ;;
        
        logs)
            show_logs
            ;;
        
        reset)
            reset_all
            ;;
        
        *)
            echo "Usage: $0 {init|start|stop|restart|status|logs|reset}"
            echo ""
            echo "Commands:"
            echo "  init      - Initialize Hermes and directory structure"
            echo "  start     - Start Docker services and Hermes backend"
            echo "  stop      - Stop Docker services"
            echo "  restart   - Restart all services"
            echo "  status    - Show service status"
            echo "  logs      - Follow Docker logs"
            echo "  reset     - Reset all data (WARNING: destructive)"
            exit 1
            ;;
    esac
}

main "$@"
