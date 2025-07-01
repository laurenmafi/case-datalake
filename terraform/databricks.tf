locals {
    databricks_admin   = "user.databricks@gmail.com"
    catalog_name       = "ifood-case"
}

data "databricks_catalog" "datalake" {
   name = "workspace"
}

resource "databricks_schema" "datalake_schemas" {
    for_each = toset([
        "bronze",
        "silver",
        "gold",
    ])

    name         = each.value
    catalog_name = data.databricks_catalog.datalake.name
}

resource "databricks_storage_credential" "datalake" {
  depends_on = [time_sleep.wait_role_creation, aws_iam_policy_attachment.bucket_access_attachment]

  name  = "datalake_storage_credential"
  owner = local.databricks_admin

  aws_iam_role {
    role_arn = aws_iam_role.storage_credential_role.arn
  }
}

resource "databricks_external_location" "bronze" {
    name            = aws_s3_bucket.bronze.id
    url             = "s3://${aws_s3_bucket.bronze.id}/"
    credential_name = databricks_storage_credential.datalake.name
    owner           = local.databricks_admin
}

resource "databricks_external_location" "silver" {
    name            = aws_s3_bucket.silver.id
    url             = "s3://${aws_s3_bucket.silver.id}/"
    credential_name = databricks_storage_credential.datalake.name
    owner           = local.databricks_admin
}

resource "databricks_external_location" "gold" {
    name            = aws_s3_bucket.gold.id
    url             = "s3://${aws_s3_bucket.gold.id}/"
    credential_name = databricks_storage_credential.datalake.name
    owner           = local.databricks_admin
}
