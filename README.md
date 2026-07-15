# GreenLeaf Bootcamp

> **DevOps exercise** — containerization, IaC, config management, and CI/CD.
> Fictional client scenario. Not a real product.

---

## What This Is

A hands-on DevOps exercise built around a realistic scenario. You'll take a
working Flask application and deploy it to AWS using industry-standard tools —
all within the AWS Free Tier (zero cost).

You'll work through four phases, each building on the previous one:

| Phase | Tool | What You'll Do | Est. Time |
|-------|------|----------------|-----------|
| 1 | Docker | Containerize the app, run it locally with Postgres | 4-5h |
| 2 | Terraform | Provision AWS infrastructure (VPC, EC2, S3) | 4-5h |
| 3 | Ansible | Configure the server and deploy the app | 4-5h |
| 4 | GitHub Actions | Automate the whole pipeline | 3-4h |

**Total: ~15-19 hours.** Designed for ~5 hours/week over 4 weeks.

---

## The Scenario

### Client Brief: GreenLeaf Recipes

> **From:** Maria @ GreenLeaf Recipes
> **Date:** July 2026
> **Subject:** We need our recipe app online — help?
>
> Hi,
>
> We're GreenLeaf — a small startup building a recipe sharing platform. Our
> developer built the backend in Python but left last week and we need to get
> it online ASAP. We have the code but no idea how to deploy it.
>
> Here's what we need:
>
> - The app needs to be accessible on the internet, just a URL people can visit
> - It stores recipes in a database — we can't lose any data if the server restarts
> - We're pre-funding so budget is basically zero for now, but we'll scale once we get users
> - Our team needs to push updates without calling someone every time — we update the recipes API pretty often
> - It has to be secure — our last dev said something about "not running as root"?
> - We work from different laptops and sometimes from home, so whatever you set up needs to be shareable
> - If something goes wrong, we need to be able to tear it all down and start over cleanly — we've been burned before
> - Oh, and we'd like some way to know the app is actually running, not just guessing
>
> We're hoping to have this live within a month. Is that doable?
>
> Thanks,
> Maria

### Your Job

Read the brief. Figure out what tools and techniques solve each of Maria's
requirements. Then build it — phase by phase.

The brief never mentions Docker, Terraform, Ansible, or CI/CD. That's the point.
Real clients describe problems, not solutions. Your job is to translate.

---

## What's Provided

The Flask application is **complete and ready to deploy**. You do not need to
modify it. It lives in `app/`:

```
app/
├── app.py              # Flask app — routes, DB connection, health check
├── requirements.txt    # Python dependencies
└── templates/
    └── index.html       # UI — recipe list + add form (Pico.css)
```

**App endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | HTML page — recipe list + add form |
| GET | `/health` | JSON health check (app + DB status) |
| GET | `/recipes` | JSON — list all recipes |
| POST | `/recipes` | JSON — create a recipe |

**Database:** PostgreSQL, single table `recipes` (id, title, ingredients, instructions, created_at)

**Environment variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `DB_HOST` | `localhost` | Postgres host |
| `DB_PORT` | `5432` | Postgres port |
| `DB_NAME` | `greenleaf` | Database name |
| `DB_USER` | `greenleaf` | Database user |
| `DB_PASSWORD` | `greenleaf` | Database password |

---

## What You Build

Everything outside `app/`:

```
greenleaf-bootcamp/
├── app/                    # PROVIDED — don't modify
├── docker/                 # PHASE 1 — you build
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
├── terraform/              # PHASE 2 — you build
│   ├── backend.tf
│   ├── vpc.tf
│   ├── ec2.tf
│   ├── outputs.tf
│   ├── variables.tf
│   └── terraform.tfvars.example
├── ansible/                # PHASE 3 — you build
│   ├── inventory.ini
│   ├── playbook.yml
│   └── roles/
│       ├── docker/
│       └── app/
├── .github/workflows/      # PHASE 4 — you build
│   └── deploy.yml
└── PHASES/                 # Your guides
    ├── phase-1-docker.md
    ├── phase-2-terraform.md
    ├── phase-3-ansible.md
    └── phase-4-cicd.md
```

---

## Prerequisites

Before you start, make sure you have:

- [ ] An AWS account (Free Tier — [sign up here](https://aws.amazon.com/free/))
- [ ] A Docker Hub account (free — [sign up here](https://hub.docker.com/))
- [ ] A GitHub account
- [ ] Docker installed locally ([install guide](https://docs.docker.com/get-docker/))
- [ ] Terraform installed locally ([install guide](https://developer.hashicorp.com/terraform/install))
- [ ] Ansible installed locally ([install guide](https://docs.ansible.com/ansible/latest/installation_guide/index.html))
- [ ] An SSH key pair for AWS (generate with `ssh-keygen -t ed25519`)

---

## Free Tier — Zero Cost Guarantee

This project is designed to cost **$0/month** on AWS. Here's the breakdown:

| Resource | Free Tier Limit | This Project Uses |
|----------|----------------|-------------------|
| EC2 t2.micro | 750h/month (1 instance 24/7) | 1 instance |
| S3 | 5GB storage | <100MB (state files) |
| Data Transfer OUT | 100GB/month | negligible |
| GitHub Actions | 2,000 min/month (private repos) | ~5-10 min/run |
| Docker Hub | Unlimited public repos | 1 repo |

**Golden rule:** Run `terraform destroy` when you're not actively working.
This ensures you never exceed Free Tier limits. The only time you need
infrastructure up is during Phase 3 (Ansible) and Phase 4 (CI/CD) testing.

---

## How to Work

1. **Fork this repo** to your own GitHub account
2. **Read each phase doc** in `PHASES/` — start with `phase-1-docker.md`
3. **Build** the deliverables for that phase
4. **Check the Definition of Done** — tick every box before moving on
5. **Commit your work** — use conventional commits (`feat(docker): add multi-stage Dockerfile`)
6. **Move to the next phase** only when the current one is fully done

You work independently. If you get stuck, that's part of the process —
research, read docs, try things. The phase docs include hints and common
gotchas to help you past the usual walls.

---

## Bonus Challenges

Finished early? Hungry for more? Check [`BONUS.md`](BONUS.md) for advanced
challenges that build on what you've done — managed databases, reverse proxies,
secrets management, and more.

---

## Client Review

After completing all four phases, write a short response to Maria. Explain what
you built and how it addresses each of her requirements — in plain language, not
tech jargon. This is a real-world skill: explaining infrastructure decisions to
non-technical stakeholders.

Put your response in `CLIENT_RESPONSE.md`.

---

## License

This is a private exercise repository. Not for distribution.