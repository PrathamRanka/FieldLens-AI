provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  apis = [
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com"
  ]
}

resource "google_project_service" "apis" {
  for_each           = toset(local.apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "docs" {
  name                        = "${var.project_id}-fieldlens-docs"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false
  depends_on                  = [google_project_service.apis]
}

resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "fieldlens"
  description   = "FieldLens container images"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

resource "google_sql_database_instance" "postgres" {
  name                = "fieldlens-postgres"
  region              = var.region
  database_version    = "POSTGRES_16"
  deletion_protection = true
  settings {
    tier            = var.db_tier
    disk_size       = 20
    disk_autoresize = true
    ip_configuration {
      ipv4_enabled = true
    }
    backup_configuration {
      enabled = true
    }
  }
  depends_on = [google_project_service.apis]
}

resource "google_sql_database" "db" {
  name     = "fieldlens"
  instance = google_sql_database_instance.postgres.name
}

data "google_secret_manager_secret_version" "db_password" {
  secret     = var.db_password_secret
  version    = var.secret_version
  depends_on = [google_project_service.apis]
}

resource "google_sql_user" "app" {
  name     = "fieldlens"
  instance = google_sql_database_instance.postgres.name
  password = data.google_secret_manager_secret_version.db_password.secret_data
}

resource "google_service_account" "runtime" {
  account_id   = "fieldlens-runtime"
  display_name = "FieldLens Cloud Run runtime"
}

resource "google_project_iam_member" "runtime_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/cloudsql.client",
    "roles/storage.objectAdmin",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter"
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_cloud_run_v2_service" "api" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"
  template {
    service_account = google_service_account.runtime.email
    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }
    containers {
      image = var.image_uri
      ports {
        container_port = 8080
      }
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
      env {
        name  = "APP_ENV"
        value = "production"
      }
      env {
        name  = "LLM_PROVIDER"
        value = "vertex"
      }
      env {
        name  = "EMBEDDING_PROVIDER"
        value = "vertex"
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }
      env {
        name  = "GCS_BUCKET"
        value = google_storage_bucket.docs.name
      }
      env {
        name  = "DATABASE_URL"
        value = "postgresql://fieldlens@/fieldlens?host=/cloudsql/${google_sql_database_instance.postgres.connection_name}"
      }
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = var.db_password_secret
            version = var.secret_version
          }
        }
      }
      env {
        name = "APP_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.api_key_secret
            version = var.secret_version
          }
        }
      }
    }
  }
  depends_on = [
    google_project_iam_member.runtime_roles,
    google_sql_user.app,
    google_project_service.apis
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public" {
  count    = var.allow_unauthenticated ? 1 : 0
  name     = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "api_url" {
  value = google_cloud_run_v2_service.api.uri
}
output "bucket_name" {
  value = google_storage_bucket.docs.name
}
output "artifact_registry" {
  value = google_artifact_registry_repository.repo.name
}
