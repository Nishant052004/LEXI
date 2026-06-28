#!/bin/bash

# Start FastAPI server on port 8000
echo "Starting FastAPI Backend Services..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Give FastAPI service a couple of seconds to initialize database and listen
sleep 3

# Start Streamlit application on port 8501 in the background (legacy UI)
echo "Starting Streamlit UI Dashboard..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

# Start Next.js AI OS Frontend on port 3000
echo "Starting Next.js AI OS Frontend on http://localhost:3000..."
cd frontend
npm run dev

