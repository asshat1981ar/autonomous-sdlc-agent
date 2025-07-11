#!/bin/bash

# Autonomous SDLC Agent Platform - Quick Start Script
# This script sets up and runs the platform for immediate use

echo "🤖 Autonomous SDLC Agent Platform - Quick Start"
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install flask flask-cors flask-sqlalchemy

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

echo "🎉 Setup complete!"
echo ""
echo "Starting services..."
echo "Backend will run on: http://localhost:5000"
echo "Frontend will run on: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the services"
echo ""

# Start backend in background
echo "🚀 Starting backend..."
python3 main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend..."
npm run dev &
FRONTEND_PID=$!

# Wait for user interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT

# Keep script running
wait