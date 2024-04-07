provider "aws" {
  region = "us-east-1"
}

locals {
    vpc_cidr = "10.0.0.0/16"
    azs = data.aws_availability_zones.available.names
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
    count = length(local.azs)
    vpc_id = aws_vpc.main.id
    cidr_block = cidrsubnet(local.vpc_cidr, length(local.azs), count.index)
    availability_zone = element(local.azs, count.index)
    tags = {
        Name = "pvt-subnet-${count.index + 1}"
    }
}

resource "aws_subnet" "public_subnets" {
    count = length(local.azs)
    vpc_id = aws_vpc.main.id
    cidr_block = cidrsubnet(local.vpc_cidr, length(local.azs), length(local.azs) + count.index)
    availability_zone = element(local.azs, count.index)
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