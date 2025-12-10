# Deployment (short)

## Render
- Uses `render.yaml` (Docker)
- Set Redis env: `REDIS_HOST`, `REDIS_PORT=6379`, `REDIS_PASSWORD` (if any), `PORT=5000`
- Push to main, create Web Service, Render builds automatically

## Fly
- Uses `fly.toml` and `.github/workflows/fly-deploy.yml`
- Required secrets: `REDIS_HOST`, `REDIS_PASSWORD`, optionally `REDIS_URL`, `REDIS_SSL`
- Deploy: push to main or run the Fly Deploy workflow

