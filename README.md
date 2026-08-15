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
