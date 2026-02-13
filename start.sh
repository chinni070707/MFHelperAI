#!/bin/bash
# MFHelper Start Script for Mac/Linux
# Run this: chmod +x start.sh && ./start.sh

echo ""
echo "🚀 Starting MFHelper..."
echo "====================="
echo ""

# Start Backend
echo "🔥 Starting Backend Server (Port 8000)..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

# Start Frontend
echo "🌐 Starting Frontend Server (Port 3000)..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

sleep 2

echo ""
echo "✅ Servers Started!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "📱 Open your browser and go to:"
echo "   http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers."
echo ""

# Trap Ctrl+C to kill both processes
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait for processes
wait
