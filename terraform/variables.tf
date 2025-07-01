variable "aws_region" {
  type        = string
  default     = "region"
}

variable "project_name" {
  type        = string
  default     = "datalake-template-project"
  description = "Name of the project for resource naming"
}

variable "databricks_host" {
    type = string
}

variable "databricks_token" {
    type = string
}

variable "databricks_account_id"{
    type    = string
}

