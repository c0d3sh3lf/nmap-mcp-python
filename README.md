# MCP Nmap FastAPI Server

A small FastAPI-based MCP-style server that runs `nmap` scans on demand.  
Provides endpoints to start scans and poll results. Ships in a Docker image and includes Kubernetes manifests.

**WARNING**: Network scanning can be illegal without authorization. Only scan hosts/networks you own or are explicitly permitted to test.

## Quick start (local)
1. Create environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Export Environment Variables:
   ```bash
   $ export SECRET_KEY=<YOURSECRETKEY> #required in prod; long random string
   $ export AUTH_USERNAME=<USERNAME> #— login username
   $ export AUTH_PASSWORD=<PASSWORD> #— login credentials
   $ export ACCESS_TOKEN_EXPIRE_MINUTES=15 #(default 15)
   $ export REFRESH_TOKEN_EXPIRE_HOURS=24 #(default 24)
   ```
3. Run:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

## Docker
Build:
```bash
docker build -t mcp-nmap-python:latest .
```

Run:
```bash
docker run -e SECRET_KEY=replace_with_long_secret_key -e AUTH_USERNAME=username -e AUTH_PASSWORD=password -e ACCESS_TOKEN_EXPIRE_MINUTES=15 -e REFRESH_TOKEN_EXPIRE_HOURS=24 -p 8080:8080 --cap-add=NET_RAW --cap-add=NET_ADMIN mcp-nmap-python:latest
```

>Note: container may need --cap-add=NET_RAW to allow certain scan types. Use with caution.

## Kubernetes

Manifests are in k8s/. Create a secret for API key and apply deployment.yaml and service.yaml. See k8s/secret.yaml for example.

## Endpoints
* `POST /auth/login` — For generating authentication tokens based on credentials
* `POST /auth/refresh` — For refreshing the access token
* `POST /scan` — start a scan (background job by default). Body: `{ "target": "1.2.3.4", "args": ["-sV","-p","80,443"], "max_seconds": 300 }`
* If you pass `?sync=true` the request will block until scan completes (not recommended for long scans).
* `GET /scan/{job_id}` — job metadata and status
* `GET /scan/{job_id}/result` — full result (XML and parsed JSON if available)
* `GET /health` — health check

## Security

* Protect the API with API_KEY env var (set API_KEY in your deployment).
* Consider network isolation for the container and strong RBAC in Kubernetes.
* Keep logs and scan results secure.

## Caveats

* This server runs the nmap binary using subprocess; ensure the container has nmap installed (Dockerfile does).
* The job store in this example is in-memory; for production use a durable store (Redis, DB, etc.).