# System Architecture

## Overview
The application follows a three-tier containerized architecture orchestrated by Docker Compose:

```text
Browser / Simulated Camera
          │  HTTP (Port 8080 -> 80)
          ▼
   [ frontend: Nginx ]
          │  Reverse Proxy (/api/ -> http://backend:5000)
          ▼
   [ backend: Flask ]
          │  TCP (Port 6379, internal Docker DNS "redis")
          ▼
   [ redis: Redis 7 ] ──► Named Volume (redis_data:/data)
```

## Design Decisions
- **Nginx Reverse Proxy**: Serving the UI and proxying `/api/` on the same origin eliminates CORS issues and avoids exposing Flask or Redis ports directly to the host machine.
- **Redis + Named Volume + AOF**: Redis provides fast in-memory sets (`parking:inside`), hashes (`parking:car:<plate>`), and lists (`parking:events`). Mounting `redis_data:/data` with `--appendonly yes` ensures state survives `docker compose down` and `docker compose up -d`.
- **Healthcheck Ordering**: `backend` uses `depends_on` with `condition: service_healthy` so Flask only starts once `redis-cli ping` succeeds.
