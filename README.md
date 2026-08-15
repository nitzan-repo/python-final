# python-final
# Platform CLI - AWS Management Tool

A comprehensive Python-based Command Line Interface (CLI) tool designed to manage AWS resources (EC2, S3, and Route53) efficiently and securely with strict adherence to tagging conventions and access control.

---

## 🚀 What the Tool Does

This CLI tool allows DevOps engineers and system administrators to provision, update, list, and delete AWS resources directly from the terminal. Key features include:
* **EC2 Operations:** Create, list, start, stop, update type, and terminate instances (with built-in safety caps).
* **S3 Operations:** Create private or public buckets (with confirmation prompts for public visibility), upload files, update visibility, list, and delete empty buckets.
* **Route53 Operations:** Create public or private Hosted Zones and manage DNS records (upsert/delete) with automated ownership tagging and verification.
* **Security & Governance:** Automatically tags all supported resources and restricts modifications or deletions exclusively to resources created by this specific CLI tool.

---

## 📋 Prerequisites

Before running the tool, ensure you have the following installed and configured:
1. **Python** (version 3.8 or higher recommended).
2. **AWS CLI** configured on your machine with appropriate permissions.
3. **AWS Credentials / Profile:** Ensure your environment has valid AWS credentials set via `aws configure` or environment variables with permissions to manage EC2, S3, Route53, and SSM Parameter Store.

---

## 📦 Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   cd python-final

*Create and activate a virtual environment (optional but recommended):
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

2. Install the required dependencies:
pip install -r requirements.txt

## 📖 Usage Examples
# General Help:
python cli.py --help
python cli.py ec2-ops --help
python cli.py s3-ops --help
python cli.py route53-ops --help

# EC2 Operations:
Create an instance (defaults to t3.micro and fetches the latest Ubuntu AMI automatically):
python cli.py ec2-ops create

Create an instance with a specific type:
python cli.py ec2-ops create --instance-type t2.small

List all CLI-created instances:
python cli.py ec2-ops list

Start an instance:
python cli.py ec2-ops start --instance-id i-0123456789abcdef0

Stop an instance:
python cli.py ec2-ops stop --instance-id i-0123456789abcdef0

Update instance type:
python cli.py ec2-ops update --instance-id i-0123456789abcdef0 --instance-type t2.small

Terminate (delete) an instance:
python cli.py ec2-ops delete --instance-id i-0123456789abcdef0

# S3 Operations
Create a private bucket:
python cli.py s3-ops create --name my-unique-bucket-123 --visibility private

Create a public bucket (triggers a confirmation warning):
python cli.py s3-ops create --name my-public-bucket-123 --visibility public

List CLI-created buckets:
python cli.py s3-ops list

Upload a file to a bucket:
python cli.py s3-ops upload --bucket my-unique-bucket-123 --file ./test.txt

Update bucket visibility:
python cli.py s3-ops update --name my-unique-bucket-123 --visibility public

Delete a bucket (must be empty):
python cli.py s3-ops delete --name my-unique-bucket-123

# Route53 Operations
Create a public Hosted Zone:
python cli.py route53-ops create-zone --name nitzan.local.

Create a private Hosted Zone (associated with a specific VPC):
python cli.py route53-ops create-zone --name internal.local. --vpc-id vpc-xxxxxxxxx

List CLI-created Hosted Zones:
python cli.py route53-ops list-zones

Create or update (Upsert) a DNS record:
python cli.py route53-ops upsert-record --zone-id Z123456789ABC --name www.nitzan.local. --type A --value 192.0.2.1

Delete a DNS record:
python cli.py route53-ops delete-record --zone-id Z123456789ABC --name www.nitzan.local. --type A --value 192.0.2.1

Delete a Hosted Zone (restricted to CLI-created zones):
python cli.py route53-ops delete-zone --zone-id Z123456789ABC

# 🏷️ Tagging Convention
To maintain strict governance, resource isolation, and safe cleanup protocols, all resources provisioned through this platform automatically include consistent tagging:
- CreatedBy: platform-cli
- Owner: nitzan

The CLI filters and blocks any management or deletion actions on resources that do not carry these exact verification tags.

# 🧹 Cleanup Instructions
To completely clean up and remove resources created by the CLI:
- Terminate EC2 instances:
python cli.py ec2-ops delete --instance-id <INSTANCE_ID>

- Empty and delete S3 buckets:
# Remove contents first, then delete the bucket
python cli.py s3-ops delete --name <BUCKET_NAME>

- Delete DNS records and Hosted Zones:
python cli.py route53-ops delete-zone --zone-id <ZONE_ID>
