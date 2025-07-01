resource "aws_s3_bucket" "bronze" {
  bucket = "${var.project_name}-bronze-zone"
  tags   = local.tags
}

resource "aws_s3_bucket" "silver"{
  bucket = "${var.project_name}-silver-zone"
  tags   = local.tags
}

resource "aws_s3_bucket" "gold"{
  bucket = "${var.project_name}-gold-zone"
  tags   = local.tags
}