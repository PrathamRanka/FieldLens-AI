variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "asia-south1"
}

variable "service_name" {
  type    = string
  default = "fieldlens-api"
}

variable "image_uri" {
  type = string
}

variable "db_password_secret" {
  type    = string
  default = "fieldlens-db-password"
}

variable "api_key_secret" {
  type    = string
  default = "fieldlens-api-key"
}

variable "secret_version" {
  type    = string
  default = "latest"
}

variable "db_tier" {
  type    = string
  default = "db-custom-1-3840"
}

variable "allow_unauthenticated" {
  type    = bool
  default = false
}
