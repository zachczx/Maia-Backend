terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.39.0"
    }
  }
}

provider "aws" {
  region     = "${var.region}"
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
}

################################################ RDS ################################################
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

################################################ OPENSEARCH ################################################

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

################################################ S3 ################################################

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

################################################ ECR ################################################

resource "aws_ecr_repository" "frontend" {
  name = "frontend-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "backend" {
  name = "backend-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_iam_policy" "allow_ecr_public_authorization" {
  name        = "AllowECRPublicAuthorization"
  description = "Policy to allow GetAuthorizationToken and GetServiceBearerToken for ECR Public"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "ecr-public:GetAuthorizationToken",
          "sts:GetServiceBearerToken"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_ecr_public_authorization_policy" {
  user       = "chulin"
  policy_arn  = aws_iam_policy.allow_ecr_public_authorization.arn
}

################################################ ECS ################################################

resource "aws_ecs_cluster" "maia" {
  name = "maia"
}

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name = "ecs-logs"
}

resource "aws_vpc" "maia" {
  cidr_block = "10.0.0.0/16"
  enable_dns_support = true
  enable_dns_hostnames = true

  tags = {
    Name = "maia-vpc"
  }
}

resource "aws_iam_policy" "allow_pass_ecs_service_role" {
  name        = "AllowPassECSServiceRole"
  description = "Policy to allow passing ecs_service_role"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "iam:PassRole",
        Effect = "Allow",
        Resource = "arn:aws:iam::339712829963:role/ecs_service_role"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_pass_ecs_service_role_policy" {
  user       = "chulin"
  policy_arn  = aws_iam_policy.allow_pass_ecs_service_role.arn
}

resource "aws_iam_role" "ecs_task_role_backend" {
  name = "ecs_task_role_backend"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_policy_backend" {
  name        = "ecs_task_policy_backend"
  description = "Policy for ECS Task to access Secrets Manager for Backend"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:${var.region}:${var.account_id}:secret:prod/maia/backend-??????"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy_backend_attachment" {
  role       = aws_iam_role.ecs_task_role_backend.name
  policy_arn  = aws_iam_policy.ecs_task_policy_backend.arn
}

resource "aws_iam_policy" "ecs_task_policy_ecr" {
  name        = "ecs_task_policy_ecr"
  description = "Policy for ECS Tasks to access ECR"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy_ecr_backend_attachment" {
  role       = aws_iam_role.ecs_task_role_backend.name
  policy_arn  = aws_iam_policy.ecs_task_policy_ecr.arn
}

resource "aws_iam_role" "ecs_task_role_frontend" {
  name = "ecs_task_role_frontend"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy_ecr_frontend_attachment" {
  role       = aws_iam_role.ecs_task_role_frontend.name
  policy_arn  = aws_iam_policy.ecs_task_policy_ecr.arn
}

resource "aws_iam_role" "ecs_service_role" {
  name = "ecs_service_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_service_policy" {
  name        = "ecs_service_policy"
  description = "Policy for ECS Service Role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "elasticloadbalancing:DescribeLoadBalancers",
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeTargetHealth"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "logs:*"
        ]
        Resource = "*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "ssm:SendCommand",
          "ssm:StartSession",
          "ssm:DescribeSessions",
          "ssm:GetConnectionStatus"
        ],
        "Resource": "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_service_policy_attachment" {
  role       = aws_iam_role.ecs_service_role.name
  policy_arn  = aws_iam_policy.ecs_service_policy.arn
}

resource "aws_ecs_task_definition" "frontend" {
  family                   = "frontend-task-family"
  execution_role_arn       = aws_iam_role.ecs_service_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role_frontend.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "frontend-container"
      image     = "${aws_ecr_repository.frontend.repository_url}:latest"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
          name          = "frontend"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"          = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"         = var.region
          "awslogs-stream-prefix"  = "frontend"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "backend-task-family"
  execution_role_arn       = aws_iam_role.ecs_service_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role_backend.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "4096"

  container_definitions = jsonencode([
    {
      name      = "backend-container"
      image     = "${aws_ecr_repository.backend.repository_url}:latest"
      cpu       = 2048
      memory    = 4096
      essential = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
          name          = "backend"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"          = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"         = var.region
          "awslogs-stream-prefix"  = "backend"
        }
      }
    }
  ])
}

resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidr_blocks)

  vpc_id            = aws_vpc.maia.id
  cidr_block        = element(var.public_subnet_cidr_blocks, count.index)
  availability_zone = element(var.availability_zones, count.index)
  map_public_ip_on_launch = true

  tags = {
    Name = "Public Subnet ${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidr_blocks)

  vpc_id            = aws_vpc.maia.id
  cidr_block        = element(var.private_subnet_cidr_blocks, count.index)
  availability_zone = element(var.availability_zones, count.index)

  tags = {
    Name = "Private Subnet ${count.index + 1}"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.maia.id

  tags = {
    Name = "Internet Gateway"
  }
}


resource "aws_route_table" "public" {
  vpc_id = aws_vpc.maia.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "Public Route Table"
  }
}

resource "aws_route_table_association" "public_subnet" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  domain = "vpc"
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  
  tags = {
    Name = "NAT Gateway"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.maia.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "Private Route Table"
  }
}

resource "aws_route_table_association" "private_subnet" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "frontend" {
  name        = "ecs_security_group_frontend"
  description = "Allow ecs traffic"
  vpc_id      = aws_vpc.maia.id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    cidr_blocks     = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "backend" {
  name        = "ecs_security_group_backend"
  description = "Allow ecs traffic"
  vpc_id      = aws_vpc.maia.id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend.id]
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_service" "frontend" {
  name            = "frontend-service"
  cluster         = aws_ecs_cluster.maia.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.public[*].id
    security_groups = [aws_security_group.frontend.id]
    assign_public_ip = true
  }
}

resource "aws_ecs_service" "backend" {
  name            = "backend-service"
  cluster         = aws_ecs_cluster.maia.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.backend.id]
    assign_public_ip = false
  }
}