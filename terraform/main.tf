provider "aws" {
  region     = "${var.region}"
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
}

resource "aws_security_group" "rds_sg" {
  name        = "rds_security_group"
  description = "Allow PostgreSQL traffic"
  vpc_id      = "${var.vpc_id}"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds_security_group"
  }
}

resource "aws_db_instance" "kb" {
  identifier             = "kb"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.5"
  username               = "${var.db_username}"
  password               = "${var.db_password}"
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  publicly_accessible    = true
  skip_final_snapshot    = true
}

resource "aws_opensearch_domain" "vector-kb" {
  domain_name    = "vector-kb"
  engine_version = "Elasticsearch_7.10"

  cluster_config {
    instance_type = "r4.large.search"
  }

  advanced_security_options {
    enabled                        = false
    anonymous_auth_enabled         = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = "${var.opensearch_username}"
      master_user_password = "${var.opensearch_password}"
    }
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }

  tags = {
    Domain = "Vector KB DB"
  }
}

resource "aws_s3_bucket" "kb_bucket" {
  bucket  = "kb-docs-bucket"
  tags    = {
    Name          = "KBDocsBucket"
    Environment   = "Production"
  }
}

resource "aws_s3_bucket_acl" "kb_bucket" {
  bucket = aws_s3_bucket.kb_bucket.id
  acl    = "private"
  depends_on = [aws_s3_bucket_ownership_controls.kb_bucket_acl_ownership]
}

resource "aws_s3_bucket_ownership_controls" "kb_bucket_acl_ownership" {
  bucket = aws_s3_bucket.kb_bucket.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket" "log_bucket" {
  bucket = "kb-log-bucket"
    tags = {
      Name        = "KBLogBucket"
      Environment = "Production"
    }
}

resource "aws_s3_bucket_acl" "log_bucket_acl" {
  bucket = aws_s3_bucket.log_bucket.id
  acl    = "log-delivery-write"
  depends_on = [aws_s3_bucket_ownership_controls.log_bucket_acl_ownership]
}

resource "aws_s3_bucket_ownership_controls" "log_bucket_acl_ownership" {
  bucket = aws_s3_bucket.log_bucket.id
  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_logging" "kb_bucket" {
  bucket        = aws_s3_bucket.kb_bucket.id
  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}