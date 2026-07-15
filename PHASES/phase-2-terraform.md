# Phase 2 — Terraform: AWS Infrastructure

> **Maria said:**
> - "the app needs to be accessible on the internet, just a URL people can visit"
> - "budget is basically zero for now"
> - "we work from different laptops — needs to be shareable"
> - "if something goes wrong, we need to tear it all down and start over cleanly"
>
> **Your job:** Provision cloud infrastructure that's reproducible, disposable,
> and costs nothing.

---

## Context

The app runs in containers locally. Now it needs a home on the internet.

You'll use Terraform to provision an EC2 instance on AWS — a virtual server
with a public IP that anyone can reach. Everything is defined as code, so
Maria's team can spin it up from any laptop and tear it down just as easily.

**Free Tier constraint:** `t2.micro` only. 750 hours/month = one instance
running 24/7. That's exactly what we need.

---

## What You Build

Create these files in `terraform/`:

### 1. `terraform/backend.tf` — Remote State

Terraform state tracks what it has created. By default it's stored locally,
but that means Maria's team can't share it across laptops. You'll use an
S3 bucket to store state remotely.

**Requirements:**
- [ ] S3 bucket for Terraform state
- [ ] Bucket name must be globally unique (e.g., `greenleaf-tfstate-<your-initials>`)
- [ ] Bucket versioning enabled (so you can roll back state)
- [ ] `backend "s3"` configuration in this file

**Note:** You need to create the S3 bucket FIRST (you can do this with
Terraform itself, or manually via AWS CLI). Then configure the backend.
This is a chicken-and-egg problem — the standard approach is to create the
bucket with a separate Terraform run or via AWS CLI, then add the backend
config. Research this, it's a common real-world pattern.

### 2. `terraform/variables.tf` — Input Variables

**Requirements:**
- [ ] `aws_region` — default `eu-central-1` (or your preferred region)
- [ ] `instance_type` — default `t2.micro`
- [ ] `ssh_key_name` — name of the SSH key pair in AWS
- [ ] `ssh_public_key` — public key content to register in AWS
- [ ] `my_ip` — your IP address for SSH security group (CIDR notation: `x.x.x.x/32`)

### 3. `terraform/vpc.tf` — Networking

**Requirements:**
- [ ] VPC (custom VPC, not default)
- [ ] One public subnet (for the EC2 instance)
- [ ] Internet Gateway attached to the VPC
- [ ] Route table with default route to the Internet Gateway
- [ ] Subnet associated with the route table
- [ ] Enable auto-assign public IP on the subnet

**Hints:**
- CIDR for VPC: `10.0.0.0/16`
- CIDR for subnet: `10.0.1.0/24`
- You know networking — this should feel familiar. The Terraform syntax
  is the new part, not the concepts.

### 4. `terraform/ec2.tf` — Compute & Security

**Requirements:**
- [ ] `t2.micro` EC2 instance in the public subnet
- [ ] Amazon Linux 2023 AMI (use the `amazon-ssm` data source or `ami-` lookup)
- [ ] Security group allowing:
  - Inbound SSH (port 22) from `var.my_ip` only
  - Inbound HTTP (port 80) from anywhere (`0.0.0.0/0`)
  - All outbound traffic
- [ ] SSH key pair registered in AWS (from `var.ssh_public_key`)
- [ ] EC2 instance uses the key pair and security group
- [ ] User data script to install Docker on first boot (saves time in Phase 3)

**Hints:**
- Use `data "aws_ami"` to find the latest Amazon Linux 2023 AMI
- User data script: install Docker and docker-compose-plugin
- The user data runs as root on first boot — perfect for Docker install
- **Package manager:** Amazon Linux 2023 uses `dnf`, not `yum` or `apt`.
  Your networking/sysadmin background will help here — it's a Fedora-based
  distro. Check the Docker docs for the AL2023-specific install steps.

### 5. `terraform/outputs.tf` — Outputs

**Requirements:**
- [ ] `instance_public_ip` — the EC2 public IP (you'll need this for Ansible)
- [ ] `instance_id` — the EC2 instance ID

### 6. `terraform/terraform.tfvars.example` — Example Variables

**Requirements:**
- [ ] Example values for all variables
- [ ] Copy to `terraform.tfvars` and fill in real values (don't commit `terraform.tfvars`)

---

## How to Test

```bash
cd terraform

# Initialize (downloads providers, configures S3 backend)
terraform init

# See what will be created
terraform plan

# Create everything
terraform apply

# Get the EC2 public IP
terraform output instance_public_ip

# SSH into the instance
ssh -i ~/.ssh/your-key ec2-user@<public-ip>

# Verify Docker was installed by user data
docker --version
docker compose version

# When done — destroy everything
terraform destroy
```

---

## Definition of Done

- [ ] `terraform init` succeeds with S3 backend configured
- [ ] `terraform plan` shows the expected resources (VPC, subnet, IGW, route table, SG, EC2, key pair)
- [ ] `terraform apply` creates all resources without errors
- [ ] `terraform output instance_public_ip` returns a public IP
- [ ] SSH into the EC2 instance works using the key pair
- [ ] Docker is installed on the EC2 (user data ran successfully)
- [ ] Security group allows SSH only from your IP (verify from a different IP if possible)
- [ ] Security group allows HTTP from anywhere
- [ ] `terraform destroy` removes everything cleanly
- [ ] No resources remain in AWS after destroy (check the AWS console)
- [ ] `terraform.tfvars` is in `.gitignore` (not committed)

---

## What You Learned

- Infrastructure as Code with Terraform
- AWS VPC networking (VPC, subnet, IGW, routing)
- EC2 provisioning and security groups
- Remote state management with S3
- Resource lifecycle (apply, destroy, reproducibility)
- User data scripts for boot-time configuration

---

## Common Gotchas

- **S3 bucket already exists** — bucket names are globally unique. If
  `greenleaf-tfstate-abc` is taken, add more characters. Use a random suffix.
- **SSH connection refused** — check the security group allows your IP on
  port 22. Also check your IP hasn't changed (home IPs can rotate).
- **AMI not found** — AMI IDs are region-specific. Use the `data "aws_ami"`
  source to look up the latest Amazon Linux 2023 AMI dynamically.
- **`terraform init` backend error** — the S3 bucket must exist before you
  configure it as a backend. Create it first, then `terraform init`.
- **Forgetting to destroy** — this is how people get surprise AWS bills. Get
  in the habit: `terraform destroy` every time you stop working.
- **Key pair already exists** — if you've used this key name before, either
  delete it in AWS or use a different name.