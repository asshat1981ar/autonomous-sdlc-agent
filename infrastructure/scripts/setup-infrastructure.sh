#!/bin/bash

# Autonomous SDLC Agent - Infrastructure Setup Script
# This script provisions the complete AWS infrastructure using Terraform

set -euo pipefail

# Configuration
PROJECT_NAME="autonomous-sdlc"
ENVIRONMENT="production"
REGION="us-west-2"
TERRAFORM_DIR="infrastructure/terraform"
STATE_BUCKET="${PROJECT_NAME}-terraform-state"
LOCK_TABLE="${PROJECT_NAME}-terraform-locks"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    local tools=("terraform" "aws" "jq")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
        fi
    done
    
    # Check Terraform version
    local tf_version
    tf_version=$(terraform version -json | jq -r '.terraform_version')
    log_info "Terraform version: $tf_version"
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid"
    fi
    
    local aws_account
    aws_account=$(aws sts get-caller-identity --query Account --output text)
    log_info "AWS Account: $aws_account"
    
    log_success "All prerequisites met"
}

# Function to setup Terraform backend
setup_terraform_backend() {
    log_info "Setting up Terraform backend..."
    
    # Create S3 bucket for Terraform state
    if aws s3 ls "s3://$STATE_BUCKET" 2>&1 | grep -q 'NoSuchBucket'; then
        log_info "Creating S3 bucket for Terraform state: $STATE_BUCKET"
        aws s3 mb "s3://$STATE_BUCKET" --region "$REGION"
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "$STATE_BUCKET" \
            --versioning-configuration Status=Enabled
        
        # Enable encryption
        aws s3api put-bucket-encryption \
            --bucket "$STATE_BUCKET" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
        
        # Block public access
        aws s3api put-public-access-block \
            --bucket "$STATE_BUCKET" \
            --public-access-block-configuration \
            BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
        
        log_success "S3 bucket created: $STATE_BUCKET"
    else
        log_warning "S3 bucket already exists: $STATE_BUCKET"
    fi
    
    # Create DynamoDB table for state locking
    if ! aws dynamodb describe-table --table-name "$LOCK_TABLE" &> /dev/null; then
        log_info "Creating DynamoDB table for state locking: $LOCK_TABLE"
        aws dynamodb create-table \
            --table-name "$LOCK_TABLE" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
            --region "$REGION"
        
        # Wait for table to be active
        aws dynamodb wait table-exists --table-name "$LOCK_TABLE" --region "$REGION"
        log_success "DynamoDB table created: $LOCK_TABLE"
    else
        log_warning "DynamoDB table already exists: $LOCK_TABLE"
    fi
}

# Function to validate Terraform configuration
validate_terraform() {
    log_info "Validating Terraform configuration..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    terraform init -upgrade
    
    # Validate configuration
    terraform validate
    
    # Format check
    if ! terraform fmt -check; then
        log_warning "Terraform files need formatting. Running terraform fmt..."
        terraform fmt
    fi
    
    cd - > /dev/null
    log_success "Terraform configuration validated"
}

# Function to plan infrastructure changes
plan_infrastructure() {
    log_info "Planning infrastructure changes..."
    
    cd "$TERRAFORM_DIR"
    
    # Create terraform plan
    terraform plan \
        -var="project_name=$PROJECT_NAME" \
        -var="environment=$ENVIRONMENT" \
        -var="region=$REGION" \
        -out=tfplan
    
    cd - > /dev/null
    log_success "Terraform plan created"
}

# Function to apply infrastructure changes
apply_infrastructure() {
    log_info "Applying infrastructure changes..."
    
    cd "$TERRAFORM_DIR"
    
    # Apply the plan
    terraform apply tfplan
    
    # Remove the plan file
    rm -f tfplan
    
    cd - > /dev/null
    log_success "Infrastructure changes applied"
}

# Function to setup AWS Load Balancer Controller
setup_alb_controller() {
    log_info "Setting up AWS Load Balancer Controller..."
    
    local cluster_name="${PROJECT_NAME}-${ENVIRONMENT}"
    
    # Update kubeconfig
    aws eks update-kubeconfig --region "$REGION" --name "$cluster_name"
    
    # Download IAM policy
    if [[ ! -f "iam_policy.json" ]]; then
        curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.0/docs/install/iam_policy.json
    fi
    
    # Create IAM policy
    local policy_arn
    policy_arn=$(aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json \
        --query 'Policy.Arn' --output text 2>/dev/null || \
        aws iam list-policies --query 'Policies[?PolicyName==`AWSLoadBalancerControllerIAMPolicy`].Arn' --output text)
    
    # Create service account
    eksctl create iamserviceaccount \
        --cluster="$cluster_name" \
        --namespace=kube-system \
        --name=aws-load-balancer-controller \
        --role-name="AmazonEKSLoadBalancerControllerRole" \
        --attach-policy-arn="$policy_arn" \
        --approve \
        --override-existing-serviceaccounts \
        --region="$REGION" || log_warning "Service account may already exist"
    
    # Install AWS Load Balancer Controller using Helm
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update
    
    helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName="$cluster_name" \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller \
        --wait
    
    # Clean up
    rm -f iam_policy.json
    
    log_success "AWS Load Balancer Controller installed"
}

# Function to setup EBS CSI Driver
setup_ebs_csi_driver() {
    log_info "Setting up EBS CSI Driver..."
    
    local cluster_name="${PROJECT_NAME}-${ENVIRONMENT}"
    
    # Create service account for EBS CSI Driver
    eksctl create iamserviceaccount \
        --name ebs-csi-controller-sa \
        --namespace kube-system \
        --cluster "$cluster_name" \
        --role-name "AmazonEKS_EBS_CSI_DriverRole" \
        --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
        --approve \
        --override-existing-serviceaccounts \
        --region="$REGION" || log_warning "EBS CSI service account may already exist"
    
    # Install EBS CSI Driver addon
    local account_id
    account_id=$(aws sts get-caller-identity --query Account --output text)
    
    aws eks create-addon \
        --cluster-name "$cluster_name" \
        --addon-name aws-ebs-csi-driver \
        --addon-version v1.23.0-eksbuild.1 \
        --service-account-role-arn "arn:aws:iam::${account_id}:role/AmazonEKS_EBS_CSI_DriverRole" \
        --resolve-conflicts OVERWRITE \
        --region "$REGION" || log_warning "EBS CSI Driver addon may already exist"
    
    log_success "EBS CSI Driver configured"
}

# Function to setup external secrets operator
setup_external_secrets() {
    log_info "Setting up External Secrets Operator..."
    
    # Add External Secrets Helm repository
    helm repo add external-secrets https://charts.external-secrets.io
    helm repo update
    
    # Install External Secrets Operator
    helm upgrade --install external-secrets external-secrets/external-secrets \
        -n external-secrets-system \
        --create-namespace \
        --wait
    
    log_success "External Secrets Operator installed"
}

# Function to create Route53 hosted zone
create_hosted_zone() {
    local domain_name="${1:-autonomous-sdlc.com}"
    log_info "Creating Route53 hosted zone for: $domain_name"
    
    # Check if hosted zone already exists
    local hosted_zone_id
    hosted_zone_id=$(aws route53 list-hosted-zones-by-name \
        --dns-name "$domain_name" \
        --query "HostedZones[?Name=='${domain_name}.'].Id" \
        --output text 2>/dev/null | cut -d'/' -f3)
    
    if [[ -z "$hosted_zone_id" ]]; then
        # Create hosted zone
        local result
        result=$(aws route53 create-hosted-zone \
            --name "$domain_name" \
            --caller-reference "$(date +%s)" \
            --hosted-zone-config Comment="Hosted zone for Autonomous SDLC Agent")
        
        hosted_zone_id=$(echo "$result" | jq -r '.HostedZone.Id' | cut -d'/' -f3)
        log_success "Hosted zone created: $hosted_zone_id"
        
        # Display name servers
        local name_servers
        name_servers=$(aws route53 get-hosted-zone --id "$hosted_zone_id" \
            --query 'DelegationSet.NameServers' --output table)
        
        log_info "Update your domain registrar with these name servers:"
        echo "$name_servers"
    else
        log_warning "Hosted zone already exists: $hosted_zone_id"
    fi
}

# Function to request SSL certificate
request_ssl_certificate() {
    local domain_name="${1:-autonomous-sdlc.com}"
    log_info "Requesting SSL certificate for: $domain_name"
    
    # Check if certificate already exists
    local cert_arn
    cert_arn=$(aws acm list-certificates \
        --query "CertificateSummaryList[?DomainName=='${domain_name}'].CertificateArn" \
        --output text 2>/dev/null)
    
    if [[ -z "$cert_arn" ]]; then
        # Request certificate
        cert_arn=$(aws acm request-certificate \
            --domain-name "$domain_name" \
            --subject-alternative-names "*.${domain_name}" \
            --validation-method DNS \
            --query 'CertificateArn' \
            --output text)
        
        log_success "SSL certificate requested: $cert_arn"
        log_info "Please validate the certificate using DNS validation"
        
        # Display validation records
        sleep 10  # Wait for validation records to be available
        aws acm describe-certificate --certificate-arn "$cert_arn" \
            --query 'Certificate.DomainValidationOptions[].ResourceRecord' \
            --output table
    else
        log_warning "SSL certificate already exists: $cert_arn"
    fi
}

# Function to output important information
output_information() {
    log_info "Gathering infrastructure information..."
    
    cd "$TERRAFORM_DIR"
    
    # Get Terraform outputs
    echo ""
    log_info "=== Infrastructure Outputs ==="
    terraform output
    
    cd - > /dev/null
    
    echo ""
    log_info "=== Next Steps ==="
    echo "1. Update your DNS settings with the Route53 name servers"
    echo "2. Validate the SSL certificate"
    echo "3. Run the deployment script: ./infrastructure/scripts/deploy.sh"
    echo "4. Configure monitoring and alerting"
    echo "5. Setup backup and disaster recovery procedures"
}

# Function to destroy infrastructure
destroy_infrastructure() {
    log_warning "This will destroy ALL infrastructure resources!"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [[ "$confirm" != "yes" ]]; then
        log_info "Infrastructure destruction cancelled"
        return 0
    fi
    
    log_warning "Destroying infrastructure in 10 seconds... (Ctrl+C to cancel)"
    sleep 10
    
    cd "$TERRAFORM_DIR"
    
    terraform destroy \
        -var="project_name=$PROJECT_NAME" \
        -var="environment=$ENVIRONMENT" \
        -var="region=$REGION" \
        -auto-approve
    
    cd - > /dev/null
    
    log_success "Infrastructure destroyed"
}

# Function to show infrastructure status
show_status() {
    log_info "Infrastructure Status"
    echo "====================="
    
    # Check Terraform state
    cd "$TERRAFORM_DIR"
    
    if [[ -f "terraform.tfstate" ]] || terraform state list &> /dev/null; then
        log_info "Terraform state exists"
        terraform state list
    else
        log_warning "No Terraform state found"
    fi
    
    cd - > /dev/null
    
    # Check AWS resources
    log_info "Checking EKS cluster..."
    aws eks describe-cluster --name "${PROJECT_NAME}-${ENVIRONMENT}" --region "$REGION" \
        --query 'cluster.status' --output text 2>/dev/null || log_warning "EKS cluster not found"
    
    log_info "Checking RDS instance..."
    aws rds describe-db-instances --db-instance-identifier "${PROJECT_NAME}-${ENVIRONMENT}-postgres" \
        --query 'DBInstances[0].DBInstanceStatus' --output text 2>/dev/null || log_warning "RDS instance not found"
}

# Main function
main() {
    local action="${1:-help}"
    
    case "$action" in
        "init")
            log_info "Initializing infrastructure setup..."
            check_prerequisites
            setup_terraform_backend
            validate_terraform
            log_success "Infrastructure initialization completed"
            ;;
        "plan")
            log_info "Planning infrastructure changes..."
            check_prerequisites
            validate_terraform
            plan_infrastructure
            ;;
        "apply")
            log_info "Applying infrastructure changes..."
            check_prerequisites
            validate_terraform
            plan_infrastructure
            apply_infrastructure
            setup_alb_controller
            setup_ebs_csi_driver
            setup_external_secrets
            output_information
            log_success "Infrastructure setup completed!"
            ;;
        "destroy")
            destroy_infrastructure
            ;;
        "status")
            show_status
            ;;
        "dns")
            DOMAIN="${2:-autonomous-sdlc.com}"
            create_hosted_zone "$DOMAIN"
            request_ssl_certificate "$DOMAIN"
            ;;
        "help"|*)
            echo "Usage: $0 {init|plan|apply|destroy|status|dns} [args...]"
            echo ""
            echo "Commands:"
            echo "  init     - Initialize Terraform backend and validate configuration"
            echo "  plan     - Plan infrastructure changes"
            echo "  apply    - Apply infrastructure changes and setup components"
            echo "  destroy  - Destroy all infrastructure"
            echo "  status   - Show current infrastructure status"
            echo "  dns      - Setup DNS and SSL certificate"
            echo ""
            echo "Examples:"
            echo "  $0 init                    - Initialize infrastructure"
            echo "  $0 plan                    - Plan changes"
            echo "  $0 apply                   - Deploy infrastructure"
            echo "  $0 dns example.com         - Setup DNS for custom domain"
            echo "  $0 status                  - Check infrastructure status"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"