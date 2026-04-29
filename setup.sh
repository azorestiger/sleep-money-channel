#!/bin/bash

# Sleep Money Affirmations - Full Setup Script
# Automates installation and initial setup

echo "🌙 Sleep Money Affirmations - Setup Script 🌙"
echo ""
echo "This script will set up your YouTube affirmations channel automation toolkit"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

echo "✓ Python $(python3 --version | awk '{print $2}') found"

# Check FFmpeg
echo ""
echo "Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found. Installing via Homebrew..."
    brew install ffmpeg
    echo "✓ FFmpeg installed"
else
    echo "✓ FFmpeg already installed"
fi

# Create directories
echo ""
echo "Creating project directories..."
mkdir -p output_videos
mkdir -p config
echo "✓ Directories created"

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Check if credentials exist
echo ""
echo "Checking YouTube API credentials..."
if [ ! -f "config/client_secrets.json" ]; then
    echo "⚠️  No client_secrets.json found"
    echo ""
    echo "To set up YouTube API:"
    echo "1. Visit: https://console.cloud.google.com/"
    echo "2. Create new project: 'Sleep Money Channel'"
    echo "3. Enable: YouTube Data API v3"
    echo "4. Create OAuth 2.0 credentials (Desktop app)"
    echo "5. Download JSON file and save as: config/client_secrets.json"
    echo ""
else
    echo "✓ YouTube API credentials found"
fi

# Test if scripts are executable
echo ""
echo "Setting up scripts..."
chmod +x scripts/*.py
echo "✓ Scripts ready"

# Display next steps
echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Set up YouTube API credentials (if not done):"
echo "   → Copy client_secrets.json to config/ folder"
echo ""
echo "2. Generate your first video:"
echo "   python3 scripts/video_generator.py --template templates/financial_abundance_8hr.json --music 'background_music.mp3'"
echo ""
echo "3. Create content schedule:"
echo "   python3 scripts/scheduler.py"
echo ""
echo "4. Upload to YouTube:"
echo "   python3 scripts/youtube_uploader.py --file 'video.mp4' --metadata 'config/metadata.json'"
echo ""
echo "📚 Documentation:"
echo "   → Start with: QUICK_START.md"
echo "   → Channel setup: CHANNEL_SETUP.md"
echo "   → Full workflow: PRODUCTION_WORKFLOW.md"
echo ""
echo "💡 More info: python3 scripts/youtube_uploader.py --help"
echo ""
