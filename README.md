# Granny's Parlor Bootcamp

> **DevOps exercise** — containerization, IaC, config management, and CI/CD.
> Fictional client scenario — Granny's Parlor is a real place, but Maria
> and her deployment troubles are invented for the exercise.

---

## What This Is

A hands-on DevOps exercise built around a fun scenario. You'll take a working
Flask application and deploy it to AWS — all within the Free Tier (zero cost).

It's aimed at anyone who knows the basics of software but has never taken
something all the way to "deployed on real infrastructure" — or who has done
pieces of it and wants to see how they connect. Fork it, work through it,
teach with it.

No deadlines. No pressure. Work at your own pace, take breaks, come back when
you feel like it. This is about exploring and learning, not racing.

---

## The Scenario

Here's the setup — you've been approached by a small startup:

---

**From:** Maria @ Granny's Parlor Recipes
**Date:** July 2026
**Subject:** We need our recipe app online — help?

Hi,

We're Granny's Parlor — a small startup building a recipe sharing platform. Our
developer built the backend in Python but left last week and we need to get it
online ASAP. We have the code but no idea how to deploy it.

Here's what we need:

- The app needs to be accessible on the internet, just a URL people can visit
- It stores recipes in a database — we can't lose any data if the server restarts
- We're pre-funding so budget is basically zero for now, but we'll scale once we get users
- Our team needs to push updates without calling someone every time — we update the recipes API pretty often
- It has to be secure — our last dev said something about "not running as root"?
- We work from different laptops and sometimes from home, so whatever you set up needs to be shareable
- If something goes wrong, we need to be able to tear it all down and start over cleanly — we've been burned before
- Oh, and we'd like some way to know the app is actually running, not just guessing

We're hoping to have this live within a month. Is that doable?

Thanks,
Maria

---

### Your Job

Read the brief. Figure out what tools and techniques solve each of Maria's
requirements. Then build it — phase by phase.

Notice something? The brief never mentions Docker, Terraform, Ansible, or
CI/CD. That's the point. Real clients describe problems, not solutions.
Your job is to translate.

---

## The Phases

Four phases, each building on the previous one. Take your time with each —
there's no rush.

| Phase | Tool | What You'll Do | Rough Time |
|-------|------|----------------|------------|
| 1 | Docker | Containerize the app, run it locally with Postgres | ~6-8h |
| 2 | Terraform | Provision AWS infrastructure (VPC, EC2, S3) | ~6-8h |
| 3 | Ansible | Configure the server and deploy the app | ~6-8h |
| 4 | GitHub Actions | Automate the whole pipeline | ~4-6h |

These are rough estimates — some phases might take you 3 hours, some might
take a week. That's fine. Life happens. Take a break, come back when you're
ready. The AWS Free Tier isn't going anywhere.

---

## What's Provided

The Flask application is **complete and ready to deploy**. You don't need to
modify it — it's just the payload you'll be deploying. It lives in `app/`:

```
app/
├── app.py              # Flask app — routes, DB connection, health check
├── requirements.txt    # Python dependencies
└── templates/
    └── index.html       # UI — recipe list + add form (Pico.css)
```

**What the app does:**

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
| `DB_NAME` | `grannysparlor` | Database name |
| `DB_USER` | `grannysparlor` | Database user |
| `DB_PASSWORD` | `grannysparlor` | Database password |

---

## What You Build

Everything outside `app/` is yours to create:

```
grannysparlor-bootcamp/
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

## Before You Start

You'll need a few accounts and tools set up. Nothing costs money:

- [ ] An AWS account (Free Tier — [sign up here](https://aws.amazon.com/free/))
- [ ] A Docker Hub account (free — [sign up here](https://hub.docker.com/))
- [ ] A GitHub account
- [ ] Docker installed locally ([install guide](https://docs.docker.com/get-docker/))
- [ ] Terraform installed locally ([install guide](https://developer.hashicorp.com/terraform/install))
- [ ] Ansible installed locally ([install guide](https://docs.ansible.com/ansible/latest/installation_guide/index.html))
- [ ] An SSH key pair for AWS (generate with `ssh-keygen -t ed25519`)

---

## Free Tier — Zero Cost

This project is designed to cost **$0/month** on AWS. Here's the breakdown:

| Resource | Free Tier Limit | This Project Uses |
|----------|----------------|-------------------|
| EC2 t2.micro | 750h/month (1 instance 24/7) | 1 instance |
| S3 | 5GB storage | <100MB (state files) |
| Data Transfer OUT | 100GB/month | negligible |
| GitHub Actions | 2,000 min/month (private repos) | ~5-10 min/run |
| Docker Hub | Unlimited public repos | 1 repo |

**One habit to build:** Run `terraform destroy` when you're done for the day.
This keeps you safely within Free Tier limits. You only need the infrastructure
up during Phase 3 (Ansible) and Phase 4 (CI/CD) testing.

---

## How to Work

1. **Fork this repo** to your own GitHub account
2. **Read each phase doc** in `PHASES/` — start with `phase-1-docker.md`
3. **Build** the deliverables for that phase
4. **Check the Definition of Done** — tick every box before moving on
5. **Commit your work** — use conventional commits (`feat(docker): add multi-stage Dockerfile`)
6. **Move to the next phase** only when you're happy with the current one

If you get stuck, that's part of the process — research, read docs, try things.
The phase docs include hints and common gotchas to help you past the usual walls.

---

## Bonus Challenges

Finished early? Curious about what's next? Check [`BONUS.md`](BONUS.md) for
advanced challenges — managed databases, reverse proxies, secrets management,
and more. All framed as "Maria got funding and needs to scale."

---

## Client Review

After completing all four phases, write a short response to Maria. Explain what
you built and how it addresses each of her requirements — in plain language, not
tech jargon. This is a real-world skill: explaining infrastructure decisions to
non-technical stakeholders.

Put your response in `CLIENT_RESPONSE.md`.

---

## License

[MIT](./LICENSE.md) — fork it, learn from it, teach with it. If it helps you,
that's what it's for.