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
  engine_version         = "15.4"
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