# Phase 3 — Ansible: Configuration & Deployment

> **Maria said:**
> - "our team needs to push updates without calling someone every time"
> - "we can't lose any data if the server restarts"
> - "it has to be secure"
>
> **Your job:** Configure the server and deploy the app in a way that's
> repeatable — run one command and the server goes from blank to live.

---

## Context

You have a fresh EC2 instance from Phase 2. Docker is installed (via user data)
but nothing else is configured. The app image is on Docker Hub from Phase 1.

Now you need to:
1. Install any missing dependencies on the server
2. Deploy the app container with the right configuration
3. Make it repeatable — one command, same result every time

Ansible is your configuration management tool. You describe the desired state
in a playbook, Ansible makes it so. Run it again, nothing changes — that's
idempotency, and it's a core concept.

---

## What You Build

Create these files in `ansible/`:

### 1. `ansible/inventory.ini` — Static Inventory

**Requirements:**
- [ ] One host group: `[webservers]`
- [ ] The EC2 public IP from Phase 2's Terraform output
- [ ] SSH user: `ec2-user`
- [ ] SSH private key path
- [ ] Python interpreter set to `/usr/bin/python3`

**Format:**
```ini
[webservers]
<ec2-public-ip> ansible_user=ec2-user ansible_ssh_private_key_file=~/.ssh/your-key
```

### 2. `ansible/playbook.yml` — Main Playbook

**Requirements:**
- [ ] Targets the `webservers` group
- [ ] Runs as `become: yes` (sudo for package installs)
- [ ] Includes/imports the roles in order: `docker`, then `app`
- [ ] Defines variables for: Docker Hub username, image name, DB credentials

### 3. `ansible/roles/docker/` — Docker Role

Ensures Docker and Docker Compose are installed and running.

**Tasks:**
- [ ] Install Docker engine (if not already — user data may have done this)
- [ ] Install docker-compose-plugin
- [ ] Ensure Docker service is enabled and started
- [ ] Add `ec2-user` to the `docker` group (so they can run Docker without sudo)
- [ ] Idempotent — running twice changes nothing

**Hint:** Amazon Linux 2023 uses `dnf`. The user data script from Phase 2
may have already installed Docker — your role should handle both cases
(already installed vs. needs install). Use `state: present` and check
service status rather than blindly reinstalling.

### 4. `ansible/roles/app/` — App Deployment Role

Deploys the Flask app container on the server.

**Tasks:**
- [ ] Create a directory for the app (e.g., `/opt/greenleaf`)
- [ ] Template a `docker-compose.yml` file from a Jinja2 template
- [ ] Pull the latest image from Docker Hub
- [ ] Run `docker compose up -d` to start the app
- [ ] Wait for the app to be healthy (poll `/health` endpoint)

**Hint:** This is NOT your Phase 1 compose. No `build` section — you pull
a pre-built image from Docker Hub. Port mapping is `80:8000`. Variables come
from Ansible (`{{ }}`), not hardcoded.

**Template: `ansible/roles/app/templates/docker-compose.yml.j2`**

**Requirements:**
- [ ] `app` service using your Docker Hub image (not a build context)
- [ ] `db` service using `postgres:16-alpine` (same as Phase 1)
- [ ] Named volume for Postgres data
- [ ] App environment variables from Ansible variables (not hardcoded)
- [ ] App port mapping: `80:8000`
- [ ] App depends on `db` being healthy
- [ ] DB healthcheck with `pg_isready`
- [ ] App restart policy: `unless-stopped`

**Hint:** Use `{{ app_image }}`, `{{ db_name }}`, `{{ db_user }}`,
`{{ db_password }}` etc. — variables defined in the playbook or group_vars.

### 5. `ansible/ansible.cfg` — Ansible Configuration

**Requirements:**
- [ ] Host key checking disabled (EC2 hosts change — `host_key_checking = False`)
- [ ] Inventory path set to `inventory.ini`
- [ ] Roles path set to `./roles`

---

## How to Test

```bash
# Make sure your EC2 is running (terraform apply from Phase 2)
cd terraform
terraform apply
terraform output instance_public_ip

# Update your Ansible inventory with the IP
cd ../ansible
# Edit inventory.ini with the EC2 public IP

# Run the playbook
ansible-playbook playbook.yml

# Test the app
curl http://<ec2-public-ip>/health
# Expected: {"database":"connected","status":"ok"}

curl http://<ec2-public-ip>/recipes
# Expected: []

# Open in browser
# http://<ec2-public-ip> — should see the recipe page

# Test idempotency — run the playbook again
ansible-playbook playbook.yml
# Expected: "changed=0" or very few changes — Ansible should detect
# everything is already in the desired state

# Test data persistence
curl -X POST http://<ec2-public-ip>/recipes \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Recipe","ingredients":"test","instructions":"test"}'

# SSH in and restart the containers
ssh -i ~/.ssh/your-key ec2-user@<ec2-public-ip>
cd /opt/greenleaf
docker compose down
docker compose up -d
exit

# Recipe should still be there
curl http://<ec2-public-ip>/recipes
```

---

## Definition of Done

- [ ] `ansible/inventory.ini` exists with EC2 IP and SSH config
- [ ] `ansible/playbook.yml` exists and includes both roles
- [ ] `ansible/roles/docker/` role installs and configures Docker
- [ ] `ansible/roles/app/` role deploys the app with a templated compose file
- [ ] `ansible/roles/app/templates/docker-compose.yml.j2` exists and uses Ansible variables
- [ ] `ansible/ansible.cfg` exists with correct configuration
- [ ] `ansible-playbook playbook.yml` completes without errors
- [ ] `curl http://<ec2-ip>/health` returns `{"status":"ok","database":"connected"}`
- [ ] `curl http://<ec2-ip>/recipes` returns `[]`
- [ ] `http://<ec2-ip>` shows the HTML page in a browser
- [ ] Creating a recipe via POST works and appears in the list
- [ ] Data persists across container restarts (volume working)
- [ ] Running the playbook twice shows idempotency (minimal or zero changes)
- [ ] App is accessible on port 80 (not 8000)

---

## What You Learned

- Configuration management with Ansible
- Playbooks, roles, and task structure
- Jinja2 templating for dynamic configuration
- Idempotency — defining desired state, not imperative commands
- Static inventory management
- Variables and variable precedence
- Ansible configuration (`ansible.cfg`)

---

## Common Gotchas

- **SSH connection fails** — verify the EC2 is running, security group allows
  your IP on port 22, and your SSH key path is correct in the inventory.
- **Permission denied on Docker** — the `ec2-user` needs to be in the `docker`
  group. After adding, you may need to reset the SSH connection or use
  `become: yes` for Docker commands until the group change takes effect.
- **Template syntax errors** — Jinja2 uses `{{ }}` for variables. If your
  compose file has `{{ }}` that aren't Ansible variables, escape them with
  `{% raw %}...{% endraw %}`.
- **App not reachable on port 80** — check the EC2 security group allows
  inbound HTTP on port 80. You set this in Phase 2's Terraform.
- **Docker compose pull fails** — make sure your Docker Hub image is public
  and the tag matches what's in your Ansible variables.
- **Idempotency issues** — if `docker compose up` reports "changed" every
  run, check if your template is generating slightly different output each
  time (whitespace, ordering). Use `changed_when` to control this if needed.