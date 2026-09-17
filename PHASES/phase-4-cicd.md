# Phase 4 — CI/CD: GitHub Actions

> **Maria said:**
> - "our team needs to push updates without calling someone every time"
> - "we update the recipes API pretty often"
>
> **Your job:** Make deployments automatic. Push to `main` → app updates on
> the server. No manual steps, no phone calls.

---

## Context

Right now, updating the app means:
1. Build the image locally
2. Push to Docker Hub manually
3. SSH into the EC2
4. Pull the new image and restart

That's fine for you, but Maria's team can't do this. You need a pipeline —
code gets pushed, everything else happens automatically.

GitHub Actions runs workflows on push events. You'll build a pipeline that
builds, pushes, and deploys — all triggered by a `git push`.

---

## What You Build

### 1. `.github/workflows/deploy.yml` — The Pipeline

**Trigger:**
- [ ] Workflow runs on push to `main` branch only
- [ ] (Optional) Also trigger manually via `workflow_dispatch`

**Job 1: Build & Push**
- [ ] Checkout code
- [ ] Login to Docker Hub (using secret `DOCKERHUB_USERNAME` + `DOCKERHUB_TOKEN`)
- [ ] Build the Docker image (use the Dockerfile from Phase 1)
- [ ] Tag the image with both `latest` and the Git commit SHA
- [ ] Push both tags to Docker Hub

**Job 2: Deploy**
- [ ] Depends on Job 1 completing successfully (`needs: build`)
- [ ] SSH into the EC2 instance using secrets
- [ ] Pull the latest image: `docker compose pull`
- [ ] Restart the app: `docker compose up -d`
- [ ] Verify the app is healthy: `curl http://localhost/health`

**Secrets to configure in GitHub:**
- [ ] `DOCKERHUB_USERNAME` — Docker Hub username
- [ ] `DOCKERHUB_TOKEN` — Docker Hub access token (not your password)
- [ ] `EC2_HOST` — EC2 public IP
- [ ] `EC2_SSH_KEY` — SSH private key contents (the entire file)
- [ ] `EC2_USER` — SSH user (`ec2-user`)

### 2. Docker Hub Access Token

Don't use your Docker Hub password. Create an access token:
- Docker Hub → Account Settings → Security → New Access Token
- Name it `grannysparlor-cicd`
- Copy the token — you'll only see it once
- Put it in GitHub Actions secrets as `DOCKERHUB_TOKEN`

---

## How to Test

```bash
# Make sure your EC2 is running and the app is deployed (Phases 2 + 3)
cd terraform
terraform apply

# Make sure Ansible has configured the server
cd ../ansible
ansible-playbook playbook.yml

# Verify the app is live
curl http://<ec2-ip>/health

# Now test the pipeline
cd ..
git add .github/workflows/deploy.yml
git commit -m "feat(cicd): add deploy workflow"
git push origin main

# Watch the pipeline run
# Go to: GitHub repo → Actions tab
# You should see your workflow running

# When it completes, verify the app updated
curl http://<ec2-ip>/health
# Should still return 200

# Make a small change to the app (e.g., change the page title)
# Push to main
# Watch the pipeline rebuild and redeploy
# Verify the change is live
```

---

## ⚠️ Forks and GitHub Actions

**If you forked this repo (recommended), GitHub Actions does NOT run
workflows automatically on forks by default.** You need to enable it:

1. Go to your forked repo on GitHub
2. Click the **Actions** tab
3. You'll see a banner saying workflows are disabled
4. Click **"I understand my workflows, go ahead and enable them"**

This is a real-world consideration — forked repos have CI disabled by
default to prevent abuse. Good to know.

---

## Definition of Done

- [ ] `.github/workflows/deploy.yml` exists
- [ ] Workflow triggers on push to `main` only
- [ ] Build job builds and pushes the Docker image to Docker Hub
- [ ] Deploy job SSHs into EC2 and restarts the app
- [ ] All required secrets are configured in GitHub
- [ ] Pushing to `main` triggers the pipeline
- [ ] Pipeline completes without errors (green checkmark)
- [ ] After pipeline runs, the app is live and healthy
- [ ] Making a code change and pushing updates the live app
- [ ] Pipeline uses Docker Hub token (not password)
- [ ] Image is tagged with commit SHA (not just `latest`)

---

## What You Learned

- CI/CD pipelines with GitHub Actions
- Workflow syntax (jobs, steps, needs, triggers)
- Secrets management in GitHub
- SSH-based deployment from CI
- Docker image tagging strategies (latest + commit SHA)
- Branch-based deployment (main = production)
- Fork behavior with GitHub Actions

---

## Common Gotchas

- **Workflow doesn't trigger on fork** — see the warning above. You must
  manually enable Actions on forked repos.
- **SSH key format in secrets** — paste the ENTIRE private key file contents
  including `-----BEGIN OPENSSH PRIVATE KEY-----` and
  `-----END OPENSSH PRIVATE KEY-----`. No trailing newline issues.
- **Docker Hub login fails** — use an access token, not your password.
  The token needs read+write permissions.
- **Deploy job can't reach EC2** — verify the EC2 is running and the
  security group allows SSH from GitHub Actions runner IPs. This is tricky
  because GitHub runners use many IPs. Options:
  - Allow SSH from `0.0.0.0/0` (less secure, fine for a learning project)
  - Use a GitHub Actions IP ranges API to restrict (advanced)
  - Use AWS Systems Manager instead of SSH (bonus challenge)
- **`docker compose` not found on EC2** — the user data script from Phase 2
  should have installed it. If not, your Ansible role from Phase 3 should
  handle it. Verify with `docker compose version` on the EC2.
- **Pipeline runs but app doesn't update** — check that the image tag in
  your EC2's compose file matches what the pipeline pushes. If the compose
  uses `latest` and the pipeline pushes `latest`, `docker compose pull`
  should get the new image. If not, you may need `docker compose up -d
  --force-recreate`.