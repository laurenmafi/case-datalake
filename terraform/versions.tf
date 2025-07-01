terraform {
  required_providers {
    aws = {
      version = "<7.0.0"
    }
    databricks = {
      source = "databricks/databricks"
      version = "<2.0.0"
    }
  }

  required_version = "< 2.0.0"
}