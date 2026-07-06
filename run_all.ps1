# Start FastAPI backend in a new window
Write-Host "Launching FastAPI Backend Services on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn main:app --host 0.0.0.0 --port 8000"

# Wait for startup
Start-Sleep -Seconds 3

# Start Streamlit Frontend in a new window (Legacy/Fallback UI)
Write-Host "Launching Streamlit Frontend Dashboard on http://localhost:8501..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run app.py --server.port 8501"

# Start Next.js AI OS Frontend (New Premium UI)
Write-Host "Launching Next.js AI OS Frontend on http://localhost:3000..." -ForegroundColor Magenta
Set-Location -Path .\frontend
npm.cmd run dev


