terraform {
  required_providers {
    spacelift = {
      source = "spacelift-io/spacelift"
    }
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "spacelift" {}

provider "aws" {
  region = "us-west-2"
}

# Needed for generating the correct role ARNs
data "aws_caller_identity" "current" {}

locals {
  role_name = "StacksSpaceLift"
  role_arn  = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${local.role_name}"
}

resource "spacelift_space" "development" {
  name = "development"
  parent_space_id = "root"
  description = "The development space."
}

resource "spacelift_stack" "stacks-dev" {
  administrative    = true
  autodeploy        = true
  branch            = "main"
  description       = "Provisions resources for Stacks"
  name              = "Stacks-Dev"
  project_root      = "terraform/stacks"
  space_id = spacelift_space.development.id
  repository        = "stacks"
  terraform_version = "1.5.7"
}

resource "spacelift_aws_integration" "this" {
  name = local.role_name
  # We need to set the ARN manually rather than referencing the role to avoid a circular dependency
  role_arn                       = local.role_arn
  generate_credentials_in_worker = false
}

data "spacelift_aws_integration_attachment_external_id" "my_stack" {
  integration_id = spacelift_aws_integration.this.id
  stack_id       = spacelift_stack.stacks-dev.id
  read           = true
  write          = true
}

# Create the IAM role, using the `assume_role_policy_statement` from the data source.
resource "aws_iam_role" "this" {
  name = local.role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      jsondecode(data.spacelift_aws_integration_attachment_external_id.my_stack.assume_role_policy_statement)
    ]
  })
}

# For our example we're granting PowerUserAccess, but you can restrict this to whatever you need.
resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
}

# Attach the integration to any stacks or modules that need to use it
resource "spacelift_aws_integration_attachment" "my_stack" {
  integration_id = spacelift_aws_integration.this.id
  stack_id       = spacelift_stack.stacks-dev.id
  read           = true
  write          = true

  # The role needs to exist before we attach since we test role assumption during attachment.
  depends_on = [
    aws_iam_role.this
  ]
}
