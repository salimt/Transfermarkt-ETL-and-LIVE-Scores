variable "credentials_path" {
  description = "The path to the credentials file"
  type        = string
  default     = "ssh key path"
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
  default     = "parma_dataset"
}

variable "gcp_dataset_location" {
  description = "GCP BigQuery dataset location"
  type        = string
  default     = "EU"
}

variable "gcp_vm_name" {
  description = "GCP VM name"
  type        = string
  default     = "parma-elt-vm"
}

variable "gcp_vm_machine_type" {
  description = "GCP VM machine type"
  type        = string
  default     = "n1-standard-2"
}

variable "gcp_vm_zone" {
  description = "GCP VM zone"
  type        = string
  default     = "southamerica-east1-c"
}

variable "gcp_vm_image" {
  description = "GCP VM image"
  type        = string
  default     = "ubuntu-2004-lts"
}

variable "gcp_vm_size" {
  description = "GCP VM size"
  type        = number
  default     = 60

}

variable "gcp_vm_network" {
  description = "GCP VM network"
  type        = string
  default     = "default"
}

variable "ssh-private-key" {
  description = "SSH private key"
  type        = string
  default     = "/keys/gcp"
}

variable "ssh-username" {
  description = "SSH username"
  type        = string
  default     = "/keys/gcp.txt"
}

variable "airflow_folder_name" {
  description = "Airflow folder name"
  type        = string
  default     = "airflow-parma"

}

variable "connection_type" {
  description = "Connection type"
  type        = string
  default     = "ssh"
}