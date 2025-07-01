locals {
    role_name = "${var.project_name}-uc-role"
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "trust_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["arn:aws:iam::414351767826:role/unity-catalog-prod-UCMasterRole-14S5ZJVKOTYTL"]
      type        = "AWS"
    }
    condition {
      test     = "StringEquals"
      variable = "sts:ExternalId"
      values   = [var.databricks_account_id]
    }
  }
  statement {
    sid     = "ExplicitSelfRoleAssumption"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
      type        = "AWS"
    }
    condition {
      test     = "ArnLike"
      variable = "aws:PrincipalArn"
      values   = [
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.role_name}"
      ]
    }
    condition {
      test     = "StringEquals"
      variable = "sts:ExternalId"
      values   = [var.databricks_account_id]
    }
  }
}

resource "aws_iam_role" "storage_credential_role" {
  name                = local.role_name
  assume_role_policy  = data.aws_iam_policy_document.trust_policy.json
  tags = local.tags
}

resource "aws_iam_policy" "allow_self_assume" {
  name = local.role_name
  policy = jsonencode({
    Version = "2012-10-17"
    Id      = local.role_name
    Statement = [
      {
        "Action" : [
          "sts:AssumeRole"
        ],
        "Resource" : [
          aws_iam_role.storage_credential_role.arn
        ],
        "Effect" : "Allow"
      }
    ]
  })
  tags = local.tags
  depends_on = [aws_iam_role.storage_credential_role]
}

resource "aws_iam_policy_attachment" "allow_self_assume_attachment" {
  name       = "Allow Storage Credential Role Self assume"
  roles      = [aws_iam_role.storage_credential_role.name]
  policy_arn = aws_iam_policy.allow_self_assume.arn
  depends_on = [aws_iam_policy.allow_self_assume, aws_iam_role.storage_credential_role]
}

data "aws_iam_policy_document" "s3_access_policy" {
  dynamic "statement" {
    for_each = toset([
        aws_s3_bucket.bronze.id,
        aws_s3_bucket.silver.id,
        aws_s3_bucket.gold.id,
    ])
    content {
      effect  = "Allow"
      actions = [
        "s3:ListBucket",
        "s3:GetBucket*",
        "s3:*Object"
      ]
      resources = [
        "arn:aws:s3:::${statement.value}",
        "arn:aws:s3:::${statement.value}/*"
      ]
    }
  }
}

resource "aws_iam_policy" "bucket_access" {
  name   = "${local.role_name}-s3-policy"
  policy = data.aws_iam_policy_document.s3_access_policy.json
  tags   = local.tags
}

resource "aws_iam_policy_attachment" "bucket_access_attachment" {
  name       = "S3 Access"
  roles      = [aws_iam_role.storage_credential_role.name]
  policy_arn = aws_iam_policy.bucket_access.arn
}

resource "time_sleep" "wait_role_creation" {
  depends_on = [aws_iam_role.storage_credential_role]

  create_duration = "60s"
}