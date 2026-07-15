# Bonus Challenges

> **6 months later — Maria's update:**
>
> "Great news — we got funding! We're scaling up. We need:
> - A proper managed database — we can't manage Postgres ourselves anymore
> - The app behind a web server — our consultant said something about reverse proxy
> - Secrets handled properly — we're storing real user data now
> - The whole team to deploy, not just one person
> - And we'd like to know what's happening on the server — logs, metrics, something"

Finished the four phases and hungry for more? These bonus challenges extend
the project with real-world scenarios. Each one is independent — pick what
interests you.

---

## Bonus 1: Managed Database (RDS)

**Maria said:** "a proper managed database"

Replace the Postgres container with AWS RDS — a managed PostgreSQL instance.

**What to do:**
- Add RDS resources to your Terraform:
  - Private subnet (your VPC needs two subnets now)
  - DB subnet group
  - RDS `t2.micro` Postgres instance
  - Security group: port 5432 only from the EC2 security group
- Update Ansible to point the app at the RDS endpoint (not the container)
- Remove the `db` service from your production compose file
- Update outputs to include the RDS endpoint

**What you learn:** Managed services, private subnets, DB subnet groups,
security group chaining (EC2 SG → RDS SG).

**Free tier:** RDS t2.micro has its own 750h/month allocation — no conflict
with your EC2 hours.

---

## Bonus 2: Nginx Reverse Proxy

**Maria said:** "behind a web server — reverse proxy"

Put Nginx in front of the Flask app. Nginx handles port 80, proxies to
the app on 8000.

**What to do:**
- Add an `nginx` role to your Ansible playbook
- Install Nginx on the EC2
- Template an Nginx config that proxies `/` to `localhost:8000`
- Use a handler to reload Nginx when config changes
- Change the app compose to expose 8000 locally only (not port 80)
- Nginx becomes the entry point on port 80

**What you learn:** Reverse proxy configuration, Ansible handlers,
Nginx templating, separating web server from app server.

---

## Bonus 3: Ansible Vault

**Maria said:** "secrets handled properly"

Stop storing DB credentials in plain text. Encrypt them with Ansible Vault.

**What to do:**
- Create `ansible/group_vars/all/vault.yml` with DB credentials
- Encrypt it: `ansible-vault encrypt group_vars/all/vault.yml`
- Create a vault password file (or use a password prompt)
- Reference vault variables in your playbook and templates
- Update your CI/CD pipeline to provide the vault password (GitHub secret)

**What you learn:** Secrets management, encryption at rest, vault password
handling, CI/CD with encrypted secrets.

---

## Bonus 4: Self-Hosted GitHub Actions Runner

**Maria said:** "the whole team to deploy"

GitHub-hosted runners are shared and rate-limited. A self-hosted runner on
your EC2 gives you unlimited minutes and full control.

**What to do:**
- Add a `runner` role to Ansible that installs the GitHub Actions runner
- Register the runner with your repo (use a registration token from GitHub)
- Configure it as a service (systemd)
- Update your workflow to use `runs-on: self-hosted` instead of
  `runs-on: ubuntu-latest`
- Remove the SSH deploy step — the runner is already on the server

**What you learn:** Self-hosted CI runners, systemd services, runner
registration, pipeline simplification.

**Free tier:** No impact — the runner runs on your existing EC2.

---

## Bonus 5: Dynamic Ansible Inventory

**What to do:**
- Write a script that reads Terraform state (or Terraform output) to
  populate the Ansible inventory dynamically
- Use `ansible-inventory` with a dynamic inventory script
- No more manually editing `inventory.ini` after `terraform apply`

**What you learn:** Dynamic inventory, Terraform-Anible integration,
inventory scripts, automation between tools.

---

## Bonus 6: Terraform State Locking

**What to do:**
- Add a DynamoDB table to your Terraform backend configuration
- Enable state locking: `use_lockfile = true` (Terraform 1.x) or
  `dynamodb_table` in the backend config
- Test: try running `terraform apply` from two terminals simultaneously

**What you learn:** State locking, concurrent state access, DynamoDB,
preventing state corruption.

**Free tier:** DynamoDB has 25GB free tier — more than enough for a
state lock table.

---

## Bonus 7: Monitoring & Logging

**Maria said:** "know what's happening on the server"

**What to do:**
- Install a lightweight monitoring stack on the EC2:
  - Prometheus (metrics) + Grafana (dashboards), or
  - Just a simple health-check cron that alerts if `/health` fails
- Set up Docker logging (json-file with size limits, or syslog)
- Create a Grafana dashboard showing:
  - App response time
  - Container status
  - Database connections

**What you learn:** Observability, metrics collection, dashboards,
log management, alerting.

**Free tier:** All these tools are open source and run on your existing EC2.

---

## How to Approach These

1. Pick ONE bonus at a time — don't stack them
2. Read the Maria quote — understand the problem before the solution
3. Research the tool/concept first
4. Implement incrementally — test after each change
5. Update your `CLIENT_RESPONSE.md` to address Maria's new requirements

These are open-ended by design. There's no single right answer — figure out
what works and defend your choices.