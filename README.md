# VIP Smart Parking (Track 2)

A containerized full-stack parking lot tracker built with Nginx, Python Flask, Redis, Docker Compose, and GitHub Actions.

## Services
- **Frontend (`frontend`)**: Nginx web server on `http://localhost:8080` serving the HTML/JS dashboard and reverse-proxying `/api/` requests to the backend.
- **Backend (`backend`)**: Python Flask REST API managing vehicle entries, exits, capacity validation (20 spots), and event logging.
- **Database (`redis`)**: `redis:7-alpine` configured with `--appendonly yes` and a named Docker volume (`redis_data`) for persistence across container restarts.

## Run Locally
1. Ensure Docker Desktop is running.
2. Validate and start all three containers:
   ```powershell
   docker compose config -q
   docker compose up -d --build
   ```
3. Open `http://localhost:8080` in your browser.

## Camera Simulation (PowerShell)
```powershell
$body = @{ plate = "123-45-678"; category = "VIP" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8080/api/cars" -Method Post -ContentType "application/json" -Body $body
Invoke-RestMethod -Uri "http://localhost:8080/api/cars" -Method Get
Invoke-RestMethod -Uri "http://localhost:8080/api/stats" -Method Get
Invoke-RestMethod -Uri "http://localhost:8080/api/cars/123-45-678/exit" -Method Post
```

## Persistence Verification
```powershell
docker compose down
docker compose up -d
```
Refresh `http://localhost:8080` to verify active vehicles remain stored. (Do not pass `-v` to `docker compose down`, as `-v` removes the `redis_data` volume.)
