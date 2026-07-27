terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }

  # Remote state is recommended for real environments. Configure and uncomment:
  # backend "s3" {
  #   bucket         = "my-tfstate-bucket"
  #   key            = "bjcf-devops-portfolio/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "bjcf-devops-portfolio"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
