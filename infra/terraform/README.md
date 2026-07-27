# Terraform — EKS platform

Provisions the platform the app runs on:

- **VPC** (`terraform-aws-modules/vpc`): 3 AZs, public + private subnets, single NAT gateway, subnet tags for the AWS Load Balancer Controller.
- **EKS** (`terraform-aws-modules/eks`): managed control plane + a managed node group in the private subnets.

## Usage

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # tweak as needed

terraform init
terraform fmt -check
terraform validate
terraform plan
terraform apply

# then point kubectl at the new cluster:
aws eks update-kubeconfig --region us-east-1 --name bjcf-portfolio
```

> ⚠️ **Cost note:** `apply` creates real, billable AWS resources (EKS control
> plane, NAT gateway, EC2 nodes). Run `terraform destroy` when you are done.
> `init` / `fmt` / `validate` are free and are what CI runs on every PR.

## Remote state

For team use, enable the S3 + DynamoDB backend stub in [`versions.tf`](versions.tf).
