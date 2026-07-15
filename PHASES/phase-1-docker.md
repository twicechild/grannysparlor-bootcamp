# Phase 1 — Containerization & Build

> **Maria said:**
> - "we can't lose any data if the server restarts"
> - "it has to be secure — not running as root"
> - "we'd like some way to know the app is actually running"
> - "we work from different laptops — needs to be shareable"
>
> **Your job:** Package the app so it runs consistently anywhere, persists data,
> reports its own health, and can be shared via a registry.

---

## Context

The app in `app/` is a Flask application that connects to PostgreSQL. Right now
it only runs if you install Python, Postgres, and all dependencies manually on
your machine. That's not reproducible and it's not shareable.

You need to containerize it — package the app and its dependencies into a
Docker image that runs identically everywhere. Then orchestrate it with
Docker Compose so the app and database start together.

---

## What You Build

Create these files in `docker/`:

### 1. `docker/Dockerfile`

Build a Docker image for the Flask app. You do NOT get a template — you write
this from scratch. Here are the requirements you must satisfy:

**Requirements checklist:**
- [ ] **Multi-stage build** — first stage installs dependencies, second stage
      is a slim runtime image (don't ship build tools to production)
- [ ] **Non-root user** — create a user in the container and run the app as
      that user (not root)
- [ ] **Healthcheck** — define a `HEALTHCHECK` that hits `/health`
- [ ] **Expose only the needed port** — the app listens on 8000
- [ ] **Copy only what's needed** — `app.py`, `requirements.txt`, `templates/`
- [ ] **Use gunicorn** — it's in `requirements.txt` for production serving
      (command: `gunicorn --bind 0.0.0.0:8000 app:app`)
- [ ] **Initialize the DB on startup** — the app calls `init_db()` on startup,
      make sure this happens before serving requests

**Hints:**
- Use `python:3.12-slim` as your base image
- `psycopg2-binary` needs no extra system packages on slim
- The working directory inside the container should be `/app`
- `pip install --no-cache-dir` keeps the image smaller
- Use `USER` directive to switch to the non-root user
- The healthcheck can use `curl` or Python's `urllib`
- **Multi-stage pip:** In the builder stage, `pip install --user` puts
  packages in `/root/.local`. In the runtime stage, copy that to the
  non-root user's home and add it to `PATH`.
- **Gunicorn loads the app differently than `python app.py`** — it imports
  the module, it doesn't run `__main__`. Check how `init_db()` is called
  in `app.py` and make sure it runs regardless of how the app starts.

### 2. `docker/docker-compose.yml`

Orchestrate the app and database together.

**Requirements:**
- [ ] Two services: `app` and `db`
- [ ] `db` uses the `postgres:16-alpine` image
- [ ] Named volume for Postgres data (so data survives container restarts)
- [ ] `db` has a healthcheck (`pg_isready`)
- [ ] `app` depends on `db` being healthy before starting
- [ ] `app` environment variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`,
      `DB_PASSWORD` — pointing to the `db` service
- [ ] `app` port mapping: `8000:8000`
- [ ] `app` builds from the `Dockerfile` in the same directory

**Hints:**
- `DB_HOST` should be `db` (the service name — Docker DNS resolves it)
- Use `depends_on` with `condition: service_healthy`
- Your Dockerfile is in `docker/` but the app code is in `app/`. The
  compose `build` section needs a `context` (the directory Docker can
  `COPY` from) and a `dockerfile` path. Pick the context so the Dockerfile
  can reach `app.py` and `templates/`.

### 3. `docker/.dockerignore`

**Requirements:**
- [ ] Exclude `.git`, `__pycache__`, `.env`, `*.pyc`, `.venv`, `node_modules`
- [ ] Exclude the `docker/` directory itself (don't copy compose files into the image)

---

## How to Test

```bash
# Build and start
cd docker
docker compose up --build

# In another terminal — test the health endpoint
curl http://localhost:8000/health
# Expected: {"database":"connected","status":"ok"}

# Test the recipes API
curl http://localhost:8000/recipes
# Expected: []

# Create a recipe
curl -X POST http://localhost:8000/recipes \
  -H "Content-Type: application/json" \
  -d '{"title":"Pasta","ingredients":"pasta, water","instructions":"boil water, cook pasta"}'

# List again
curl http://localhost:8000/recipes
# Expected: [{"id":1,"title":"Pasta",...}]

# Open in browser
# http://localhost:8000 — you should see the recipe list and add form

# Test data persistence
docker compose down        # stop containers (NOT -v)
docker compose up          # start again
curl http://localhost:8000/recipes
# Expected: recipe still there — volume persisted the data

# Clean up
docker compose down -v     # -v removes the volume too
```

---

## Push to Docker Hub

Once your image works locally, tag and push it:

```bash
# Tag it
docker tag <your-image-name> <your-dockerhub-username>/greenleaf:latest

# Login
docker login

# Push
docker push <your-dockerhub-username>/greenleaf:latest
```

You'll need this image in Phase 3 (Ansible pulls it on the server) and
Phase 4 (CI/CD pushes new versions).

---

## Definition of Done

- [ ] `docker/Dockerfile` exists and satisfies all requirements in the checklist
- [ ] `docker/docker-compose.yml` exists and satisfies all requirements
- [ ] `docker/.dockerignore` exists and excludes the right files
- [ ] `docker compose up --build` starts both services without errors
- [ ] `curl localhost:8000/health` returns `{"status":"ok","database":"connected"}`
- [ ] `curl localhost:8000/recipes` returns `[]`
- [ ] Creating a recipe via POST works and appears in the list
- [ ] `http://localhost:8000` shows the HTML page with recipes
- [ ] Data persists across `docker compose down` (without `-v`) and `up`
- [ ] `docker compose down -v` cleans up everything
- [ ] Image is tagged and pushed to Docker Hub
- [ ] Container runs as a non-root user (verify with `docker exec <container> whoami`)

---

## What You Learned

- Building optimized Docker images (multi-stage, slim base)
- Container security (non-root user)
- Health checks for container orchestration
- Docker Compose for multi-service orchestration
- Data persistence with named volumes
- Container registries (Docker Hub)

---

## Common Gotchas

- **`psycopg2-binary` import error** — make sure you're using `python:3.12-slim`
  or similar. If you use `alpine`, you'll need additional system packages for
  psycopg2. Stick with `slim` to avoid this.
- **App can't connect to DB** — `DB_HOST` must be `db` (the service name), not
  `localhost`. Inside the container, `localhost` is the container itself.
- **App starts before DB is ready** — use `depends_on` with
  `condition: service_healthy`. The `pg_isready` healthcheck on the DB service
  is essential.
- **`init_db()` not called under gunicorn** — gunicorn imports the module
  instead of running `__main__`. If the first request crashes with
  `relation "recipes" does not exist`, this is why.