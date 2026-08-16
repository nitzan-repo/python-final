# Platform CLI & UI - AWS Management Tool

A comprehensive Python-based Command Line Interface (CLI) tool designed to manage AWS resources (EC2, S3, and Route53).

---

## 🚀 What the Tool Does

This CLI & UI tool allows to provision, update, list, and delete AWS resources directly from the terminal or from a user-friendly UI interface. Key features include:
* **EC2 Operations:** Create, list, start, stop, update type, and terminate instances (with built-in safety caps).
* **S3 Operations:** Create private or public buckets (with confirmation prompts for public visibility), upload files, update visibility, list, and delete empty buckets.
* **Route53 Operations:** Create public or private Hosted Zones and manage DNS records (upsert/delete) with automated ownership tagging and verification.
* **Web UI Dashboard:** An interactive Streamlit-based graphical user interface that wraps all management operations into easy-to-use forms and screens.
* **Security:** Automatically tags all supported resources and restricts modifications or deletions exclusively to resources created by this specific CLI tool.

---

## 📋 Prerequisites

Before running the tool, ensure you have the following installed and configured:
1. **Python** (version 3.8 or higher recommended).
2. **AWS Credentials / Profile:** Ensure your environment has valid AWS credentials set via `aws configure` or environment variables with permissions to manage EC2, S3, Route53, and SSM Parameter Store.

---

## 📦 Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   cd python-final

**Create and activate a virtual environment (optional but recommended):**
create:
   ```bash
   python -m venv .venv
```

activate:
*On Windows (PowerShell):*
   ```bash
   .venv\Scripts\Activate.ps1
  ```
*On macOS/Linux:*
   ```bash
   source .venv/bin/activate
  ```

2. Install the required dependencies:
  ```bash
   pip install -r requirements.txt
  ```
## 📖 CLI Usage Examples
# General Help:
```bash
python cli.py --help
```
```bash
python cli.py ec2-ops --help
```
```bash
python cli.py s3-ops --help
```
```bash
python cli.py route53-ops --help
```

### EC2 Operations:

* Create an instance (defaults to `t3.micro` and fetches the latest Ubuntu AMI automatically):
    ```bash
    python cli.py ec2-ops create
    ```
* Create an instance with a specific type:
    ```bash
    python cli.py ec2-ops create --instance-type t2.small
    ```
* List all CLI-created instances:
    ```bash
    python cli.py ec2-ops list
    ```
* Start an instance:
    ```bash
    python cli.py ec2-ops start --instance-id i-0123456789abcdef0
    ```
* Stop an instance:
    ```bash
    python cli.py ec2-ops stop --instance-id i-0123456789abcdef0
    ```
* Update instance type:
    ```bash
    python cli.py ec2-ops update --instance-id i-0123456789abcdef0 --instance-type t2.small
    ```
* Terminate (delete) an instance:
    ```bash
    python cli.py ec2-ops delete --instance-id i-0123456789abcdef0
    ```

### S3 Operations

* Create a private bucket:
    ```bash
    python cli.py s3-ops create --name my-unique-bucket-123 --visibility private
    ```
* Create a public bucket (triggers a confirmation warning):
    ```bash
    python cli.py s3-ops create --name my-public-bucket-123 --visibility public
    ```
* List CLI-created buckets:
    ```bash
    python cli.py s3-ops list
    ```
* Upload a file to a bucket:
    ```bash
    python cli.py s3-ops upload --bucket my-unique-bucket-123 --file ./test.txt
    ```
* Update bucket visibility:
    ```bash
    python cli.py s3-ops update --name my-unique-bucket-123 --visibility public
    ```
* Delete a bucket (must be empty):
    ```bash
    python cli.py s3-ops delete --name my-unique-bucket-123
    ```

### Route53 Operations

* Create a public Hosted Zone:
    ```bash
    python cli.py route53-ops create-zone --name nitzan.local.
    ```
* Create a private Hosted Zone (associated with a specific VPC):
    ```bash
    python cli.py route53-ops create-zone --name internal.local. --vpc-id vpc-xxxxxxxxx
    ```
* List CLI-created Hosted Zones:
    ```bash
    python cli.py route53-ops list-zones
    ```
* Create or update (Upsert) a DNS record:
    ```bash
    python cli.py route53-ops upsert-record --zone-id Z123456789ABC --name www.nitzan.local. --type A --value 192.0.2.1
    ```
* Delete a DNS record:
    ```bash
    python cli.py route53-ops delete-record --zone-id Z123456789ABC --name www.nitzan.local. --type A --value 192.0.2.1
    ```
* Delete a Hosted Zone (restricted to CLI-created zones):
    ```bash
    python cli.py route53-ops delete-zone --zone-id Z123456789ABC
    ```
# 💻 Running the UI
To launch the interactive Streamlit web dashboard:

Ensure all your manager files (ec2_manager.py, s3_manager.py, route53_manager.py) and the UI file (app.py) are in the same directory.

Run the following command in your terminal:
streamlit run app.py

Open the local URL provided in your terminal (usually http://localhost:8501) in your web browser.


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
** Remove contents first, then delete the bucket **
python cli.py s3-ops delete --name <BUCKET_NAME>

- Delete DNS records and Hosted Zones:
python cli.py route53-ops delete-zone --zone-id <ZONE_ID>
