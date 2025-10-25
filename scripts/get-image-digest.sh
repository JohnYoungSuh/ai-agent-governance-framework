#!/bin/bash
# get-image-digest.sh - Helper script to retrieve Docker image digests
# Usage: ./scripts/get-image-digest.sh <image:tag>

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get digest using docker
get_digest_docker() {
    local image="$1"
    local platform="${2:-linux/amd64}"

    print_info "Pulling image: $image (platform: $platform)"

    if docker pull "$image" --platform "$platform" >/dev/null 2>&1; then
        local digest=$(docker inspect "$image" --format='{{index .RepoDigests 0}}' 2>/dev/null | cut -d'@' -f2)

        if [ -n "$digest" ]; then
            echo "$digest"
            return 0
        fi
    fi

    return 1
}

# Function to get digest using crane (faster, no pull required)
get_digest_crane() {
    local image="$1"

    print_info "Fetching digest with crane (no pull required)"

    if command_exists crane; then
        crane digest "$image" 2>/dev/null || return 1
    else
        return 1
    fi
}

# Function to get digest using docker buildx
get_digest_buildx() {
    local image="$1"

    print_info "Fetching digest with docker buildx"

    if command_exists docker && docker buildx version >/dev/null 2>&1; then
        docker buildx imagetools inspect "$image" --format '{{json .Manifest.Digest}}' 2>/dev/null | tr -d '"' || return 1
    else
        return 1
    fi
}

# Function to format devcontainer.json snippet
format_devcontainer_snippet() {
    local image="$1"
    local digest="$2"

    echo ""
    print_success "Image digest retrieved successfully!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Digest: ${GREEN}$digest${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "devcontainer.json snippet:"
    echo ""
    echo '{'
    echo "  \"image\": \"$image@$digest\""
    echo '}'
    echo ""
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 <image:tag> [options]

Retrieves the SHA256 digest for a Docker image to use in devcontainer.json

Options:
  -p, --platform PLATFORM   Specify platform (default: linux/amd64)
  -m, --method METHOD       Force specific method: crane, buildx, or docker
  -h, --help               Show this help message

Examples:
  $0 openapitools/openapi-generator-cli:v7.2.0
  $0 mcr.microsoft.com/devcontainers/python:3.11 --platform linux/arm64
  $0 bufbuild/buf:latest --method crane

Methods (tried in order if not specified):
  1. crane   - Fastest, no image pull required (install: go install github.com/google/go-containerregistry/cmd/crane@latest)
  2. buildx  - Fast, uses docker buildx imagetools
  3. docker  - Slower, requires pulling full image

Why use digests?
  - Ensures reproducible builds
  - Prevents tag mutation issues
  - Required for security compliance
  - Reduces rebuild variability

Token savings:
  Using pinned vendor images vs custom builds saves ~96% tokens per rebuild

Documentation:
  See: docs/DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md

EOF
}

# Main function
main() {
    local image=""
    local platform="linux/amd64"
    local method=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -p|--platform)
                platform="$2"
                shift 2
                ;;
            -m|--method)
                method="$2"
                shift 2
                ;;
            -*)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                image="$1"
                shift
                ;;
        esac
    done

    # Validate image argument
    if [ -z "$image" ]; then
        print_error "No image specified"
        echo ""
        show_usage
        exit 1
    fi

    # Add :latest tag if no tag specified
    if [[ ! "$image" =~ : ]]; then
        print_warning "No tag specified, using :latest"
        image="${image}:latest"
    fi

    print_info "Image: $image"
    echo ""

    local digest=""

    # Try specified method or all methods in order
    if [ -n "$method" ]; then
        case "$method" in
            crane)
                digest=$(get_digest_crane "$image") || true
                ;;
            buildx)
                digest=$(get_digest_buildx "$image") || true
                ;;
            docker)
                digest=$(get_digest_docker "$image" "$platform") || true
                ;;
            *)
                print_error "Unknown method: $method"
                echo "Valid methods: crane, buildx, docker"
                exit 1
                ;;
        esac
    else
        # Try crane first (fastest)
        digest=$(get_digest_crane "$image") || true

        # Fall back to buildx
        if [ -z "$digest" ]; then
            digest=$(get_digest_buildx "$image") || true
        fi

        # Fall back to docker pull
        if [ -z "$digest" ]; then
            digest=$(get_digest_docker "$image" "$platform") || true
        fi
    fi

    # Check if we got a digest
    if [ -z "$digest" ]; then
        echo ""
        print_error "Failed to retrieve digest for: $image"
        echo ""
        echo "Troubleshooting:"
        echo "  1. Verify image exists: docker pull $image"
        echo "  2. Check authentication: docker login"
        echo "  3. Install crane for faster lookups:"
        echo "     go install github.com/google/go-containerregistry/cmd/crane@latest"
        echo ""
        exit 1
    fi

    # Format and display output
    format_devcontainer_snippet "$image" "$digest"

    # Show method used
    if command_exists crane && [ -z "$method" ]; then
        print_info "Method: crane (fast, no pull)"
    elif docker buildx version >/dev/null 2>&1 && [ -z "$method" ]; then
        print_info "Method: buildx imagetools"
    else
        print_info "Method: docker pull"
    fi

    # Show recommendation to install crane
    if ! command_exists crane; then
        echo ""
        print_warning "Tip: Install 'crane' for faster digest lookups (no image pull):"
        echo "  go install github.com/google/go-containerregistry/cmd/crane@latest"
    fi

    echo ""
}

# Run main function
main "$@"
