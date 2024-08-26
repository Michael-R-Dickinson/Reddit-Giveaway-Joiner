variable region {
  type = string
  default = "us-central1"
}

variable backend_bucket {
  type = string
  default = "reddit-giveaway-terraform-backend"
}

# Reddit API credentials
variable reddit_client_id {
  type = string
  sensitive = true
}
variable reddit_client_secret {
  type = string
  sensitive = true
}
variable reddit_username {
  type = string
  sensitive = true
}
variable reddit_password {
  type = string
  sensitive = true
}

# Openai API credentials
variable openai_api_key {
  type = string
  sensitive = true
}