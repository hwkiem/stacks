provider "aws" {
    region = "us-east-1"
}

locals {
    vpc_cidr = "10.0.0.0/16"
    max_azs = 2
    azs = data.aws_availability_zones.available
    vpc_azs = slice(local.all_azs.names, 0, min(local.max_azs, length(local.all_azs.names)))
}

data "aws_availability_zones" "available" {
    state = "available"
}

resource "aws_vpc" "main" {
    cidr_block = local.vpc_cidr
    tags = {
        Name = "Stacks-VPC"
    }
}

resource "aws_subnet" "private_subnets" {
    count = length(local.vpc_azs)
    vpc_id = aws_vpc.main.id
    cidr_block = cidrsubnet(local.vpc_cidr, length(local.vpc_azs), count.index)
    availability_zone = element(local.vpc_azs, count.index)
    tags = {
        Name = "pvt-subnet-${count.index + 1}"
    }
}

resource "aws_subnet" "public_subnets" {
    count = length(local.vpc_azs)
    vpc_id = aws_vpc.main.id
    cidr_block = cidrsubnet(local.vpc_cidr, length(local.vpc_azs), length(local.vpc_azs) + count.index)
    availability_zone = element(local.vpc_azs, count.index)
    tags = {
        Name = "pub-subnet-${count.index + 1}"
    }
}

resource "aws_internet_gateway" "gw" {
    vpc_id = aws_vpc.main.id
    tags = {
        Name = "Stacks-igw"
    }
}

resource "aws_route_table" "public_rt" {
    vpc_id = aws_vpc.main.id
 
    route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
    }
 
    tags = {
        Name = "Internet Route Table"
    }
}

resource "aws_route_table_association" "public_rt_association" {
    count = length(local.vpc_azs)
    subnet_id      = element(aws_subnet.public_subnets[*].id, count.index)
    route_table_id = aws_route_table.public_rt.id
}

resource "aws_ecr_repository" "stacks_repo" {
  name                 = "stacks-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_iam_role" "ecsTaskExecutionRole" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = "${data.aws_iam_policy_document.assume_role_policy.json}"
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecsTaskExecutionRole_policy" {
  role       = "${aws_iam_role.ecsTaskExecutionRole.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_cluster" "stacks_cluster" {
  name = "stacks-cluster"
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "app-first-task" # Name your task
  container_definitions    = <<DEFINITION
  [
    {
      "name": "app-first-task",
      "image": "${aws_ecr_repository.stacks_repo.repository_url}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "hostPort": 5000
        }
      ],
      "memory": 512,
      "cpu": 256
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = 512
  cpu                      = 256
  execution_role_arn       = "${aws_iam_role.ecsTaskExecutionRole.arn}"
}

resource "aws_security_group" "load_balancer_security_group" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow traffic in from all sources
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_alb" "application_load_balancer" {
  name               = "stacks-api-alb" #load balancer name
  load_balancer_type = "application"
  subnets = aws_subnet.public_subnets[*].id
  # security group
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
}

resource "aws_lb_target_group" "target_group" {
  name        = "target-group"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = "${aws_vpc.main.id}" # default VPC
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = "${aws_alb.application_load_balancer.arn}" #  load balancer
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = "${aws_lb_target_group.target_group.arn}" # target group
  }
}

