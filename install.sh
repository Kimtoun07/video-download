#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  GrabVid Installer for Linux & macOS
# ═══════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "   ╔══════════════════════════════════════╗"
echo "   ║  🎬 GrabVid Installer               ║"
echo "   ║  Universal Video Downloader          ║"
echo "   ╚══════════════════════════════════════╝"
echo -e "${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed.${NC}"
    echo "  Install it from: https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "  ${GREEN}✓${NC} Python ${PYTHON_VERSION} detected"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 is not installed.${NC}"
    echo "  Install it with: python3 -m ensurepip"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} pip3 detected"

# Check ffmpeg
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -1)
    echo -e "  ${GREEN}✓${NC} ffmpeg detected: ${FFMPEG_VERSION}"
else
    echo -e "  ${YELLOW}⚠${NC} ffmpeg not found (required for video processing)"
    echo "  Install with:"
    echo "    Ubuntu/Debian: ${CYAN}sudo apt install ffmpeg${NC}"
    echo "    macOS:         ${CYAN}brew install ffmpeg${NC}"
    echo "    Fedora:        ${CYAN}sudo dnf install ffmpeg${NC}"
    echo "    Arch:          ${CYAN}sudo pacman -S ffmpeg${NC}"
    echo ""
fi

# Parse arguments
INSTALL_GUI=false
INSTALL_ALL=false
INSTALL_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --gui) INSTALL_GUI=true; shift ;;
        --all) INSTALL_ALL=true; shift ;;
        --dir) INSTALL_DIR="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --gui     Install with GUI support"
            echo "  --all     Install all optional dependencies"
            echo "  --dir DIR Install to specific directory"
            echo "  --help    Show this help"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Determine install directory
if [ -z "$INSTALL_DIR" ]; then
    INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
fi

echo ""
echo -e "  ${BLUE}▶${NC} Installing GrabVid from: ${INSTALL_DIR}"
echo ""

# Install
cd "$INSTALL_DIR"

echo -e "  ${CYAN}Installing core dependencies...${NC}"
pip3 install --upgrade yt-dlp click 2>/dev/null || pip3 install --user --upgrade yt-dlp click

if [ "$INSTALL_GUI" = true ] || [ "$INSTALL_ALL" = true ]; then
    echo -e "  ${CYAN}Installing GUI dependencies...${NC}"
    pip3 install --upgrade customtkinter Pillow 2>/dev/null || pip3 install --user --upgrade customtkinter Pillow
fi

if [ "$INSTALL_ALL" = true ]; then
    echo -e "  ${CYAN}Installing optional dependencies...${NC}"
    pip3 install --upgrade pyperclip mutagen requests 2>/dev/null || pip3 install --user --upgrade pyperclip mutagen requests
fi

# Install the package itself
echo -e "  ${CYAN}Installing GrabVid package...${NC}"
pip3 install -e . 2>/dev/null || pip3 install --user -e .

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ GrabVid installed successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo -e "  ${PURPLE}Usage:${NC}"
echo -e "    ${CYAN}grabvid <url>${NC}              Download a video"
echo -e "    ${CYAN}grabvid batch <file>${NC}       Batch download"
echo -e "    ${CYAN}grabvid episodes <url>${NC}     Download playlist"
echo -e "    ${CYAN}grabvid info <url>${NC}         Show video info"
echo -e "    ${CYAN}grabvid gui${NC}                Launch GUI"
echo -e "    ${CYAN}grabvid platforms${NC}          List platforms"
echo ""
echo -e "  ${PURPLE}Quick start:${NC}"
echo -e "    ${CYAN}grabvid https://youtube.com/watch?v=example${NC}"
echo ""
