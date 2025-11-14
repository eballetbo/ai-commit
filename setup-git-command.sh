#!/bin/bash
# Setup script to install ai-commit as a git command

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Commit Git Command Setup ===${NC}\n"

# Check if we're in the right directory
if [ ! -f "ai-commit.py" ]; then
    echo -e "${YELLOW}Error: ai-commit.py not found in current directory${NC}"
    echo "Please run this script from the ai-commit repository root"
    exit 1
fi

# Step 1: Check dependencies
echo -e "${BLUE}Step 1: Checking dependencies...${NC}"
if ! python3 -c "import google.generativeai" 2>/dev/null; then
    echo -e "${YELLOW}google-generativeai not installed. Installing...${NC}"
    pip install -q google-generativeai || pip3 install -q google-generativeai
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already satisfied${NC}"
fi

# Step 2: Rename and make executable
echo -e "\n${BLUE}Step 2: Preparing git command script...${NC}"
if [ ! -f "git-ai-commit" ]; then
    cp ai-commit.py git-ai-commit
    echo -e "${GREEN}✓ Created git-ai-commit${NC}"
fi

chmod +x git-ai-commit
echo -e "${GREEN}✓ Script is executable${NC}"

# Step 3: Install to PATH
echo -e "\n${BLUE}Step 3: Installing to PATH...${NC}"

# Try user-level first (recommended, no sudo)
if [ -d "$HOME/.local/bin" ]; then
    cp git-ai-commit "$HOME/.local/bin/"
    INSTALL_PATH="$HOME/.local/bin"
    echo -e "${GREEN}✓ Installed to $INSTALL_PATH${NC}"

    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
        echo -e "${GREEN}✓ ~/.local/bin is already in PATH${NC}"
    else
        echo -e "${YELLOW}⚠ ~/.local/bin is not in your PATH${NC}"
        echo "Add this to your ~/.bashrc or ~/.zshrc:"
        echo -e "${BLUE}  export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
        echo "Then run: source ~/.bashrc"
    fi
else
    # Fallback to /usr/local/bin (requires sudo)
    echo -e "${YELLOW}Creating ~/.local/bin...${NC}"
    mkdir -p "$HOME/.local/bin"
    cp git-ai-commit "$HOME/.local/bin/"
    INSTALL_PATH="$HOME/.local/bin"
    echo -e "${GREEN}✓ Installed to $INSTALL_PATH${NC}"
fi

# Step 4: Configure API key (optional)
echo -e "\n${BLUE}Step 4: API Key Configuration${NC}"
if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${YELLOW}GOOGLE_API_KEY not set${NC}"
    echo "Get your API key from: https://aistudio.google.com/app/apikey"
    echo -e "\nAdd to your ~/.bashrc or ~/.zshrc:"
    echo -e "${BLUE}  export GOOGLE_API_KEY='your-api-key-here'${NC}"
    echo "Then run: source ~/.bashrc"
else
    echo -e "${GREEN}✓ GOOGLE_API_KEY is already configured${NC}"
fi

# Step 5: Verify installation
echo -e "\n${BLUE}Step 5: Verifying installation...${NC}"

# Refresh PATH for this script
export PATH="$INSTALL_PATH:$PATH"

if command -v git-ai-commit &> /dev/null; then
    echo -e "${GREEN}✓ git-ai-commit is available in PATH${NC}"
    echo -e "\n${BLUE}You can now use:${NC}"
    echo -e "  ${GREEN}git ai-commit${NC}              # Interactive mode"
    echo -e "  ${GREEN}git ai-commit --help${NC}       # Show help"
    echo -e "  ${GREEN}git ai-commit --auto-commit${NC} # Auto-commit"
    echo -e "  ${GREEN}git ai-commit --dry-run${NC}     # Preview only"
else
    echo -e "${YELLOW}⚠ git-ai-commit not yet in PATH (may need shell restart)${NC}"
    echo "Run in a new terminal, or:"
    echo -e "${BLUE}  export PATH=\"$INSTALL_PATH:\$PATH\"${NC}"
    echo -e "  ${GREEN}git ai-commit --help${NC}"
fi

echo -e "\n${GREEN}=== Setup Complete ===${NC}\n"
