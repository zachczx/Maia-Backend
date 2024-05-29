provider "aws" {
  region     = "${var.region}"
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
}

resource "aws_db_instance" "faq" {
  identifier             = "faq"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15.4"
  username               = "${var.db_username}"
  password               = "${var.db_password}"
  publicly_accessible    = false
  skip_final_snapshot    = true

  tags = {
    Name = "DB for FAQ Microservice"
  }
}