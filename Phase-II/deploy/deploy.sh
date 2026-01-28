#!/bin/bash

# Deployment script for Todo Application Backend
# This script handles the deployment of the Todo Application to various environments

set -e  # Exit immediately if a command exits with a non-zero status

# Default values
ENVIRONMENT="production"
DOCKER_BUILD_ARGS=""
SKIP_TESTS="false"
FORCE_DEPLOY="false"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Deploy the Todo Application Backend"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Target environment (default: production)"
    echo "  -b, --build-args ARGS    Additional Docker build arguments"
    echo "  --skip-tests             Skip running tests before deployment"
    echo "  --force                  Force deployment even if tests fail"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                      # Deploy to production"
    echo "  $0 -e staging                          # Deploy to staging"
    echo "  $0 --skip-tests                        # Deploy without running tests"
    echo "  $0 -e development --skip-tests         # Deploy dev without tests"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build-args)
            DOCKER_BUILD_ARGS="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS="true"
            shift
            ;;
        --force)
            FORCE_DEPLOY="true"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Valid environments: development, staging, production"
    exit 1
fi

print_info "Starting deployment to $ENVIRONMENT environment..."

# Check if required tools are available
command -v docker >/dev/null 2>&1 || { print_error "docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { print_error "docker-compose is required but not installed. Aborting."; exit 1; }

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    print_error ".env file not found in current directory"
    exit 1
else
    print_info ".env file found"
fi

# Run tests if not skipped
if [[ "$SKIP_TESTS" == "false" ]]; then
    print_info "Running tests before deployment..."

    # Set test environment variables
    export ENVIRONMENT=test
    export NEON_DB_URL="sqlite:///./test.db"

    if python -m pytest tests/ -v; then
        print_info "All tests passed"
    else
        if [[ "$FORCE_DEPLOY" == "true" ]]; then
            print_warn "Tests failed but --force flag is set, continuing deployment..."
        else
            print_error "Tests failed. Deployment cancelled. Use --force to override."
            exit 1
        fi
    fi

    # Reset environment variables
    unset ENVIRONMENT
    unset NEON_DB_URL
else
    print_warn "Skipping tests as requested"
fi

# Build the Docker image
print_info "Building Docker image..."
if [[ -n "$DOCKER_BUILD_ARGS" ]]; then
    docker build $DOCKER_BUILD_ARGS -t todo-app-backend:$ENVIRONMENT .
else
    docker build -t todo-app-backend:$ENVIRONMENT .
fi

if [[ $? -ne 0 ]]; then
    print_error "Docker build failed"
    exit 1
fi

print_info "Docker image built successfully"

# Tag image for registry if needed
if [[ "$ENVIRONMENT" == "production" ]] || [[ "$ENVIRONMENT" == "staging" ]]; then
    # You can customize this for your registry
    # For example: docker tag todo-app-backend:$ENVIRONMENT your-registry/todo-app:$ENVIRONMENT
    print_info "Image tagged for $ENVIRONMENT deployment"
fi

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose down || true

# Update docker-compose.yml for environment
print_info "Starting deployment with docker-compose..."
ENVIRONMENT=$ENVIRONMENT docker-compose up -d

if [[ $? -eq 0 ]]; then
    print_info "Deployment to $ENVIRONMENT completed successfully!"
    print_info "Application should be available shortly"

    # Wait a bit and check if the app is running
    sleep 10

    if docker-compose ps | grep -q "Up"; then
        print_info "Service is running"
        docker-compose logs --tail=20
    else
        print_error "Service may not be running properly"
        docker-compose logs
        exit 1
    fi
else
    print_error "Deployment failed"
    docker-compose logs
    exit 1
fi

print_info "Deployment process finished"