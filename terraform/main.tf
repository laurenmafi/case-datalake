provider "aws" {
    region  = var.aws_region
}

provider "databricks" {
    host  = var.databricks_host
    token = var.databricks_token
}

locals {
  tags = {
    project = "ifood-case"
    env = "dev"
  }
}