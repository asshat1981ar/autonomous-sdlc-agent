#!/bin/bash

# Autonomous SDLC Agent - Production Deployment Script
# This script automates the complete deployment process for the production environment

set -euo pipefail

# Configuration
CLUSTER_NAME="autonomous-sdlc-production"
REGION="us-west-2"
NAMESPACE="production"
ENVIRONMENT="production"
IMAGE_REGISTRY="ghcr.io"
IMAGE_REPOSITORY="autonomous-sdlc/autonomous-sdlc-agent"

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
    local tools=("kubectl" "aws" "helm" "docker")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed or not in PATH"
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid"
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
    fi
    
    log_success "All prerequisites met"
}

# Function to configure kubectl
configure_kubectl() {
    log_info "Configuring kubectl for EKS cluster..."
    
    aws eks update-kubeconfig \
        --region "$REGION" \
        --name "$CLUSTER_NAME" \
        --alias "$CLUSTER_NAME"
    
    # Verify connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Failed to connect to Kubernetes cluster"
    fi
    
    log_success "kubectl configured successfully"
}

# Function to create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace "$NAMESPACE"
        kubectl label namespace "$NAMESPACE" environment="$ENVIRONMENT"
        log_success "Namespace $NAMESPACE created"
    fi
}

# Function to deploy secrets
deploy_secrets() {
    log_info "Deploying secrets..."
    
    # Check if secrets file exists
    local secrets_file="k8s/production/secrets.yaml"
    if [[ ! -f "$secrets_file" ]]; then
        log_error "Secrets file not found: $secrets_file"
    fi
    
    # Validate that placeholder values have been replaced
    if grep -q "REPLACE_WITH_ACTUAL" "$secrets_file"; then
        log_error "Secrets file contains placeholder values. Please update with actual secrets."
    fi
    
    kubectl apply -f "$secrets_file" -n "$NAMESPACE"
    log_success "Secrets deployed"
}

# Function to deploy ConfigMaps
deploy_configmaps() {
    log_info "Deploying ConfigMaps..."
    
    kubectl apply -f k8s/production/configmap.yaml -n "$NAMESPACE"
    log_success "ConfigMaps deployed"
}

# Function to build and push Docker image
build_and_push_image() {
    local version="${1:-latest}"
    log_info "Building and pushing Docker image: $version"
    
    # Build image
    docker build -t "$IMAGE_REGISTRY/$IMAGE_REPOSITORY:$version" -f docker/Dockerfile .
    
    # Push image
    docker push "$IMAGE_REGISTRY/$IMAGE_REPOSITORY:$version"
    
    log_success "Docker image built and pushed: $IMAGE_REGISTRY/$IMAGE_REPOSITORY:$version"
}

# Function to deploy application
deploy_application() {
    local version="${1:-latest}"
    log_info "Deploying application components..."
    
    # Update image tags in deployment files
    local temp_dir=$(mktemp -d)
    cp -r k8s/production/* "$temp_dir/"
    
    # Replace image tags
    find "$temp_dir" -name "*.yaml" -exec sed -i "s|image: ghcr.io/autonomous-sdlc/autonomous-sdlc-agent:latest|image: $IMAGE_REGISTRY/$IMAGE_REPOSITORY:$version|g" {} +
    
    # Deploy API
    kubectl apply -f "$temp_dir/api-deployment.yaml" -n "$NAMESPACE"
    
    # Deploy Workers
    kubectl apply -f "$temp_dir/worker-deployment.yaml" -n "$NAMESPACE"
    
    # Deploy Ingress
    kubectl apply -f "$temp_dir/ingress.yaml" -n "$NAMESPACE"
    
    # Clean up temp directory
    rm -rf "$temp_dir"
    
    log_success "Application components deployed"
}

# Function to wait for deployment rollout
wait_for_rollout() {
    log_info "Waiting for deployment rollout to complete..."
    
    local deployments=("autonomous-sdlc-api" "autonomous-sdlc-worker" "autonomous-sdlc-scheduler")
    
    for deployment in "${deployments[@]}"; do
        log_info "Waiting for $deployment to be ready..."
        kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=600s
    done
    
    log_success "All deployments rolled out successfully"
}

# Function to run health checks
run_health_checks() {
    log_info "Running health checks..."
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app=autonomous-sdlc-api -n "$NAMESPACE" --timeout=300s
    
    # Get service endpoint
    local service_ip
    service_ip=$(kubectl get service autonomous-sdlc-api -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    if [[ -z "$service_ip" ]]; then
        service_ip=$(kubectl get service autonomous-sdlc-api -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
        log_warning "LoadBalancer not ready, using ClusterIP for health check: $service_ip"
    fi
    
    # Health check with retry
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        if kubectl exec -n "$NAMESPACE" deployment/autonomous-sdlc-api -- curl -f "http://localhost:8000/health" &> /dev/null; then
            log_success "Health check passed"
            return 0
        fi
        
        sleep 10
        ((attempt++))
    done
    
    log_error "Health check failed after $max_attempts attempts"
}

# Function to run smoke tests
run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # Create test pod
    kubectl run smoke-test \
        --image="$IMAGE_REGISTRY/$IMAGE_REPOSITORY:latest" \
        --rm -i --restart=Never \
        -n "$NAMESPACE" \
        -- python -c "
import requests
import sys

try:
    # Test API health endpoint
    response = requests.get('http://autonomous-sdlc-api:80/health', timeout=10)
    response.raise_for_status()
    print('✅ API health check passed')
    
    # Test A2A framework endpoint
    response = requests.get('http://autonomous-sdlc-api:80/api/v1/agents/health', timeout=10)
    response.raise_for_status()
    print('✅ A2A framework health check passed')
    
    print('✅ All smoke tests passed')
    sys.exit(0)
except Exception as e:
    print(f'❌ Smoke test failed: {e}')
    sys.exit(1)
" || log_error "Smoke tests failed"
    
    log_success "Smoke tests passed"
}

# Function to setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Add Prometheus Helm repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Install Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set prometheus.prometheusSpec.retention=30d \
        --set grafana.adminPassword=admin \
        --wait
    
    # Install metrics server if not exists
    if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
        kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    fi
    
    log_success "Monitoring setup completed"
}

# Function to create backup job
create_backup_job() {
    log_info "Creating backup CronJob..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: $NAMESPACE
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: database-credentials
                  key: password
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h \$DATABASE_HOST -U \$DATABASE_USER \$DATABASE_NAME | gzip > /backup/backup-\$(date +%Y%m%d-%H%M%S).sql.gz
              aws s3 cp /backup/ s3://autonomous-sdlc-backups/database/ --recursive
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            emptyDir: {}
          restartPolicy: OnFailure
EOF
    
    log_success "Backup CronJob created"
}

# Function to display deployment summary
display_summary() {
    log_info "Deployment Summary"
    echo "===================="
    echo "Cluster: $CLUSTER_NAME"
    echo "Namespace: $NAMESPACE"
    echo "Environment: $ENVIRONMENT"
    echo "Image: $IMAGE_REGISTRY/$IMAGE_REPOSITORY:${VERSION:-latest}"
    echo ""
    
    log_info "Service Endpoints:"
    kubectl get services -n "$NAMESPACE" -o wide
    
    echo ""
    log_info "Pod Status:"
    kubectl get pods -n "$NAMESPACE" -o wide
    
    echo ""
    log_info "Deployment Status:"
    kubectl get deployments -n "$NAMESPACE"
    
    echo ""
    log_success "Deployment completed successfully!"
    log_info "You can monitor the application at: https://autonomous-sdlc.com"
    log_info "Monitor logs with: kubectl logs -f deployment/autonomous-sdlc-api -n $NAMESPACE"
}

# Function to rollback deployment
rollback_deployment() {
    local deployment="${1:-autonomous-sdlc-api}"
    log_warning "Rolling back deployment: $deployment"
    
    kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE"
    kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=300s
    
    log_success "Rollback completed for $deployment"
}

# Function to cleanup failed deployment
cleanup_failed_deployment() {
    log_warning "Cleaning up failed deployment..."
    
    # Delete all resources in the namespace
    kubectl delete all --all -n "$NAMESPACE" || true
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    local version="${1:-latest}"
    local skip_build="${2:-false}"
    
    log_info "Starting deployment of Autonomous SDLC Agent"
    log_info "Version: $version"
    log_info "Environment: $ENVIRONMENT"
    
    # Set trap for cleanup on failure
    trap 'log_error "Deployment failed! Run with --rollback to revert changes"' ERR
    
    check_prerequisites
    configure_kubectl
    create_namespace
    
    if [[ "$skip_build" != "true" ]]; then
        build_and_push_image "$version"
    fi
    
    deploy_secrets
    deploy_configmaps
    deploy_application "$version"
    wait_for_rollout
    run_health_checks
    run_smoke_tests
    setup_monitoring
    create_backup_job
    
    display_summary
    
    log_success "🎉 Deployment completed successfully!"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        VERSION="${2:-latest}"
        SKIP_BUILD="${3:-false}"
        main "$VERSION" "$SKIP_BUILD"
        ;;
    "rollback")
        DEPLOYMENT="${2:-autonomous-sdlc-api}"
        rollback_deployment "$DEPLOYMENT"
        ;;
    "cleanup")
        cleanup_failed_deployment
        ;;
    "health-check")
        run_health_checks
        ;;
    "smoke-test")
        run_smoke_tests
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|cleanup|health-check|smoke-test} [args...]"
        echo ""
        echo "Commands:"
        echo "  deploy [version] [skip-build]  - Deploy the application (default: latest, false)"
        echo "  rollback [deployment]          - Rollback a deployment (default: autonomous-sdlc-api)"
        echo "  cleanup                        - Cleanup failed deployment"
        echo "  health-check                   - Run health checks"
        echo "  smoke-test                     - Run smoke tests"
        echo ""
        echo "Examples:"
        echo "  $0 deploy v1.2.3              - Deploy version v1.2.3"
        echo "  $0 deploy latest true          - Deploy latest version without building"
        echo "  $0 rollback autonomous-sdlc-worker - Rollback worker deployment"
        exit 1
        ;;
esac