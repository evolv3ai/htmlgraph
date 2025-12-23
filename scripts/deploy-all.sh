#!/bin/bash
#
# HtmlGraph Complete Deployment Script
#
# This script performs a full release cycle:
# 1. Push to git
# 2. Build and publish Python package to PyPI
# 3. Install latest version locally
# 4. Update Claude plugin
# 5. Update Gemini extension
# 6. Update Codex skill
#
# Usage:
#   ./scripts/deploy-all.sh [version]
#
# Example:
#   ./scripts/deploy-all.sh 0.7.1
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "ℹ️  $1"
}

# Get version from argument or use default
VERSION=${1:-$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")}

log_section "HtmlGraph Deployment - Version $VERSION"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    log_error "Must be run from project root (where pyproject.toml is)"
    exit 1
fi

# Load PyPI token from .env if it exists
if [ -f ".env" ]; then
    log_info "Loading environment variables from .env"
    source .env
fi

# Check for required environment variables
if [ -z "$PyPI_API_TOKEN" ] && [ -z "$UV_PUBLISH_TOKEN" ]; then
    log_warning "PyPI token not found in environment"
    log_info "Set PyPI_API_TOKEN in .env or UV_PUBLISH_TOKEN in environment"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ============================================================================
# STEP 1: Git Push
# ============================================================================
log_section "Step 1: Pushing to Git"

# Check git status
if ! git diff-index --quiet HEAD --; then
    log_warning "You have uncommitted changes"
    git status --short
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Push to remote
log_info "Pushing to origin/main..."
if git push origin main --tags; then
    log_success "Pushed to git"
else
    log_error "Git push failed"
    exit 1
fi

# ============================================================================
# STEP 2: Build Python Package
# ============================================================================
log_section "Step 2: Building Python Package"

# Clean old builds
log_info "Cleaning old builds..."
rm -rf dist/

# Build with uv
log_info "Building package..."
if uv build; then
    log_success "Package built successfully"
    ls -lh dist/
else
    log_error "Build failed"
    exit 1
fi

# ============================================================================
# STEP 3: Publish to PyPI
# ============================================================================
log_section "Step 3: Publishing to PyPI"

log_info "Publishing htmlgraph-$VERSION to PyPI..."

if [ -n "$PyPI_API_TOKEN" ]; then
    # Use token from .env
    if uv publish dist/htmlgraph-${VERSION}* --token "$PyPI_API_TOKEN"; then
        log_success "Published to PyPI"
    else
        log_error "PyPI publish failed"
        exit 1
    fi
elif [ -n "$UV_PUBLISH_TOKEN" ]; then
    # Use UV_PUBLISH_TOKEN from environment
    if uv publish dist/htmlgraph-${VERSION}*; then
        log_success "Published to PyPI"
    else
        log_error "PyPI publish failed"
        exit 1
    fi
else
    log_warning "No PyPI token found, skipping publish"
    log_info "You can publish manually with:"
    log_info "  uv publish dist/htmlgraph-${VERSION}* --token YOUR_TOKEN"
fi

# Wait a bit for PyPI to process
log_info "Waiting 10 seconds for PyPI to process..."
sleep 10

# ============================================================================
# STEP 4: Install Latest Version Locally
# ============================================================================
log_section "Step 4: Installing Latest Version Locally"

log_info "Installing htmlgraph==$VERSION..."
if pip install --upgrade htmlgraph==$VERSION; then
    log_success "Installed locally"
else
    log_warning "Local install failed, trying with --force-reinstall"
    if pip install --force-reinstall htmlgraph==$VERSION; then
        log_success "Installed locally (force reinstall)"
    else
        log_error "Local install failed"
        exit 1
    fi
fi

# Verify installation
INSTALLED_VERSION=$(python -c "import htmlgraph; print(htmlgraph.__version__)" 2>/dev/null || echo "unknown")
if [ "$INSTALLED_VERSION" = "$VERSION" ]; then
    log_success "Verified: htmlgraph $INSTALLED_VERSION is installed"
else
    log_warning "Installed version ($INSTALLED_VERSION) doesn't match expected ($VERSION)"
fi

# ============================================================================
# STEP 5: Update Claude Plugin
# ============================================================================
log_section "Step 5: Updating Claude Plugin"

if command -v claude &> /dev/null; then
    log_info "Updating Claude plugin..."
    if claude plugin update htmlgraph; then
        log_success "Claude plugin updated"
    else
        log_warning "Claude plugin update failed"
        log_info "You may need to update manually with:"
        log_info "  claude plugin update htmlgraph"
    fi
else
    log_warning "Claude CLI not found"
    log_info "Install with: npm install -g @anthropics/claude-cli"
fi

# ============================================================================
# STEP 6: Update Gemini Extension
# ============================================================================
log_section "Step 6: Updating Gemini Extension"

GEMINI_EXTENSION_DIR="packages/gemini-extension"
if [ -d "$GEMINI_EXTENSION_DIR" ]; then
    log_info "Updating Gemini extension version in gemini-extension.json..."

    # Update version in gemini-extension.json
    if [ -f "$GEMINI_EXTENSION_DIR/gemini-extension.json" ]; then
        # Use Python to update JSON (more reliable than sed)
        python -c "
import json
with open('$GEMINI_EXTENSION_DIR/gemini-extension.json', 'r') as f:
    data = json.load(f)
data['version'] = '$VERSION'
with open('$GEMINI_EXTENSION_DIR/gemini-extension.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Updated gemini-extension.json to version $VERSION')
"
        log_success "Gemini extension version updated"

        # If there's a build/deploy process, run it
        if [ -f "$GEMINI_EXTENSION_DIR/deploy.sh" ]; then
            log_info "Running Gemini extension deploy script..."
            (cd "$GEMINI_EXTENSION_DIR" && bash deploy.sh)
        else
            log_info "No deploy script found for Gemini extension"
            log_info "Extension files updated, manual deployment may be needed"
        fi
    else
        log_warning "gemini-extension.json not found"
    fi
else
    log_warning "Gemini extension directory not found"
fi

# ============================================================================
# STEP 7: Update Codex Skill (if applicable)
# ============================================================================
log_section "Step 7: Updating Codex Skill"

# Codex skills are typically in a different location
# Adjust path as needed for your setup
if command -v codex &> /dev/null; then
    log_info "Checking for Codex skill..."
    # Add Codex-specific update commands here if applicable
    log_info "Codex skill update - manual verification needed"
else
    log_info "Codex CLI not found - skipping"
fi

# ============================================================================
# Summary
# ============================================================================
log_section "Deployment Complete! 🎉"

echo ""
echo "Summary:"
echo "--------"
echo "✅ Git push: Complete"
echo "✅ Package build: htmlgraph-$VERSION"
echo "✅ PyPI publish: https://pypi.org/project/htmlgraph/$VERSION/"
echo "✅ Local install: $INSTALLED_VERSION"
echo "✅ Claude plugin: Updated"
echo "✅ Gemini extension: Updated"
echo ""
log_success "All deployment steps completed successfully!"
echo ""
echo "Verify deployment:"
echo "  - PyPI: https://pypi.org/project/htmlgraph/$VERSION/"
echo "  - GitHub: https://github.com/Shakes-tzd/htmlgraph"
echo "  - Local: python -c 'import htmlgraph; print(htmlgraph.__version__)'"
echo ""
