# Define the required providers
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.15.0"
    }
  }
}

# Define the provider
provider "google" {
  credentials = file(var.credentials_path)
  project     = var.project_name
  region      = var.gcp_region
}


# Create the GCP bucket
resource "google_storage_bucket" "parma-project" {
  name          = var.gcp_bucket_name
  location      = var.gcp_bucket_location
  force_destroy = var.gcp_bucket_force_destroy
  lifecycle_rule {
    condition {
      age = var.gcp_bucket_lifetime_rule_age
    }
    action {
      type = var.gcp_bucket_action_type
    }
  }
}

# Create the BigQuery dataset
resource "google_bigquery_dataset" "parma-dataset" {
  dataset_id                 = var.gcp_dataset_name
  location                   = var.gcp_dataset_location
  delete_contents_on_destroy = true
}



# Create the BigQuery table for market value history
resource "google_bigquery_table" "market_value_history" {
  dataset_id = google_bigquery_dataset.parma-dataset.dataset_id
  table_id   = "market_value_history"
  deletion_protection = false
}

## Create the BigQuery table for players
resource "google_bigquery_table" "players" {
    dataset_id = google_bigquery_dataset.parma-dataset.dataset_id
    table_id   = "profiles"
    deletion_protection = false
}

## Create the BigQuery table for stats
resource "google_bigquery_table" "players" {
    dataset_id = google_bigquery_dataset.parma-dataset.dataset_id
    table_id   = "players_stats"
    deletion_protection = false
}