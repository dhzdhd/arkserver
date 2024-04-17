# Ark Server

A Ark SE server setup using Docker and a bunch of IaC to setup the server on AWS.

## Setup

- AWS
  - Create a AWS key pair
  - Create a AWS IAM user & set appropriate permissions
  - Install AWS CLI and run `aws configure`

## Create and run

- Pulumi
  - `cd iac/pulumi`
  - Create resources with `pulumi up`
  - Destroy with `pulumi destroy`
