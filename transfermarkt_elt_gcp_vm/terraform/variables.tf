variable "credentials_path" {
  description = "The path to the credentials file"
  type        = string
  default     = "ssh private key path"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "parma-data-elt"
}

variable "gcp_region" {
  description = "GCP region to deploy resources in"
  type        = string
  default     = "eu-west1"
}

variable "gcp_bucket_name" {
  description = "GCP bucket name"
  type        = string
  default     = "parma-project-terra-bucket"
}

variable "gcp_bucket_location" {
  description = "GCP bucket location"
  type        = string
  default     = "EU"
}

variable "gcp_bucket_storage_class" {
  description = "GCP bucket storage class"
  type        = string
  default     = "STANDARD"
}

variable "gcp_bucket_lifetime_rule_age" {
  description = "GCP bucket lifetime rule age"
  type        = number
  default     = 60
}

variable "gcp_bucket_force_destroy" {
  description = "GCP bucket force destroy"
  type        = bool
  default     = true
}

variable "gcp_bucket_action_type" {
  description = "GCP bucket action type"
  type        = string
  default     = "AbortIncompleteMultipartUpload"
}

variable "gcp_dataset_name" {
  description = "GCP BigQuery dataset name"
  type        = string
  default     = "transfermarkt_analytics"
}

variable "gcp_dataset_location" {
  description = "GCP BigQuery dataset location"
  type        = string
  default     = "EU"
}