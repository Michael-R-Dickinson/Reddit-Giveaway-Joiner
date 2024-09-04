terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }

  backend "gcs" {
    bucket = var.backend_bucket
  }
}

provider "google" {
  # Yeah yeah best practices
  project = "reddit-giveaways"
  region = var.region
}

# Backend bucket
resource "google_storage_bucket" "terraform_state" {
  name = var.backend_bucket
  location = "US"

  versioning {
    enabled = true
  }

  lifecycle {
    prevent_destroy = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
}

# Creating the Cron Lambda that this whole thing's about

resource "google_storage_bucket" "function_code_bucket" {
  name     = "reddit-giveaways-function-code" 
  location = "US" 
}

resource "google_storage_bucket_object" "function_zip" {
  name   = "function-${filemd5("${path.module}/function_export.zip")}.zip"
  bucket = google_storage_bucket.function_code_bucket.name
  source = "${path.module}/function_export.zip"
}

resource "google_cloudfunctions_function" "cron_lambda" {
  name        = "reddit-giveaways-cron"

  runtime     = "python312"
  entry_point = "main"

  source_archive_bucket = google_storage_bucket.function_code_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip.name

  timeout = "60"

  environment_variables = {
    CLIENT_ID=var.reddit_client_id
    CLIENT_SECRET=var.reddit_client_secret
    REDDIT_USERNAME=var.reddit_username
    REDDIT_PASSWORD=var.reddit_password
    OPENAI_API_KEY=var.openai_api_key
  }
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource = google_pubsub_topic.cron_topic.name
  }
}

resource google_pubsub_topic cron_topic {
  name = "reddit-giveaways-cron-topic"
}

resource google_cloud_scheduler_job cron_job {
  name = "reddit-giveaways-cron-job"
  schedule = "3 6,18 * * *"
  time_zone = "UTC"

  pubsub_target {
    topic_name = google_pubsub_topic.cron_topic.id
    data = base64encode("trigger giveaway function")
  }
}

# The bucket to save our joined giveaway log in 

resource "google_storage_bucket" "giveaways_data_bucket" {
  name     = "reddit-giveaways-giveaway-data" 
  location = "US" 
}

resource "google_storage_bucket_object" "giveaway_log" {
  name   = "giveaway_log.txt"
  bucket = google_storage_bucket.giveaways_data_bucket.name
  source = "${path.module}/giveaway_log_seed.txt"

  # Tells tofu not to replace the file with my local copy after the inital upload
  lifecycle {
    ignore_changes = [ source ]
  }
}

resource "google_storage_bucket_iam_member" "giveaways_data_bucket_reader" {
  bucket = google_storage_bucket.giveaways_data_bucket.name
  role = "roles/storage.admin"
  member = "serviceAccount:${google_cloudfunctions_function.cron_lambda.service_account_email}"
}