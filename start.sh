#!/bin/bash
set -e

# Port configuration (Render assigns $PORT, fallback to 3000)
PORT="${PORT:-3000}"

# Start FastAPI backend server on port 8000 in background
echo "Starting FastAPI Backend Services on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Give FastAPI service a couple of seconds to initialize database and listen
sleep 3

# Start Streamlit application on port 8501 in the background (unless disabled)
if [ "${DISABLE_STREAMLIT}" != "true" ]; then
  echo "Starting Streamlit UI Dashboard on port 8501..."
  streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true &
fi

# Start Next.js AI OS Frontend on the public Render web service port
echo "Starting Next.js AI OS Frontend on port ${PORT}..."
cd frontend
exec npm run start -- -p "${PORT}" -H 0.0.0.0
