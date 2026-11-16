# GCP Terraform deployment

Prerequisites: billing-enabled GCP project, Terraform >=1.5, gcloud, and a secret named `fieldlens-db-password` in Secret Manager.

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
echo -n 'A-strong-db-password' | gcloud secrets create fieldlens-db-password --data-file=-
echo -n 'A-long-random-api-key' | gcloud secrets create fieldlens-api-key --data-file=-
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# edit project_id, region, image_uri, db_password_secret_version
terraform init
terraform plan
terraform apply
```

Build and push the backend image (replace region/project):

```bash
gcloud builds submit ../../backend --tag REGION-docker.pkg.dev/PROJECT_ID/fieldlens/fieldlens-api:latest
```

Set `image_uri` to that image and apply again. Terraform creates Cloud SQL (PostgreSQL), a GCS bucket, Artifact Registry, runtime service account, and Cloud Run service. Enable Cloud SQL connector access and initialise the schema using a controlled migration job or Cloud SQL Auth Proxy. The Cloud Run service reads database and API credentials from Secret Manager. The API applies the SQL schema at startup. The invoker policy is private by default.

Before public use: add domain, auth (IAP/OIDC), Cloud Armor/rate limits, VPC egress controls, database backups/PITR, monitoring alerts, and tenant-level data access controls.


**Cost warning:** Cloud SQL is billable even when idle. The default `db-custom-1-3840` tier is not a free-tier configuration. Check current regional pricing, use a temporary development instance, and destroy resources when finished (after backing up anything you need). Terraform enables deletion protection on the database instance, so disable that deliberately before destroying it.
