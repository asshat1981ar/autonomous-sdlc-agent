#!/bin/bash

# Autonomous SDLC Agent Platform Deployment Script
# This script deploys the platform to Kubernetes using Helm

set -e

# Configuration
NAMESPACE=${NAMESPACE:-"sdlc-agent"}
RELEASE_NAME=${RELEASE_NAME:-"sdlc-agent"}
CHART_PATH=${CHART_PATH:-"helm/sdlc-agent"}
VALUES_FILE=${VALUES_FILE:-"values.yaml"}
ENVIRONMENT=${ENVIRONMENT:-"production"}

echo "🚀 Deploying Autonomous SDLC Agent Platform"
echo "============================================="
echo "Environment: ${ENVIRONMENT}"
echo "Namespace: ${NAMESPACE}"
echo "Release: ${RELEASE_NAME}"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is required but not installed."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ Helm is required but not installed."
    exit 1
fi

# Verify cluster connection
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create namespace if it doesn't exist
echo "📦 Setting up namespace..."
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Add required labels to namespace
kubectl label namespace ${NAMESPACE} name=${NAMESPACE} --overwrite

# Install or upgrade cert-manager if needed
echo "🔐 Setting up cert-manager..."
if ! kubectl get namespace cert-manager &> /dev/null; then
    echo "Installing cert-manager..."
    kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    kubectl wait --for=condition=ready pod -l app=cert-manager --timeout=300s -n cert-manager
fi

# Install nginx-ingress if needed
echo "🌐 Setting up nginx-ingress..."
if ! kubectl get namespace ingress-nginx &> /dev/null; then
    echo "Installing nginx-ingress..."
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm repo update
    helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer
fi

# Validate Helm chart
echo "🔧 Validating Helm chart..."
helm lint ${CHART_PATH}

# Deploy using Helm
echo "🚀 Deploying SDLC Agent Platform..."

case ${ENVIRONMENT} in
    "staging")
        VALUES_ARGS="--values ${CHART_PATH}/values.yaml --values ${CHART_PATH}/values-staging.yaml"
        ;;
    "production")
        VALUES_ARGS="--values ${CHART_PATH}/values.yaml --values ${CHART_PATH}/values-production.yaml"
        ;;
    *)
        VALUES_ARGS="--values ${CHART_PATH}/values.yaml"
        ;;
esac

helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
    --namespace ${NAMESPACE} \
    ${VALUES_ARGS} \
    --wait \
    --timeout=10m \
    --atomic

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/sdlc-backend -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=600s deployment/sdlc-frontend -n ${NAMESPACE}

# Get service information
echo "📋 Deployment Information:"
echo "=========================="

# Get ingress information
INGRESS_IP=$(kubectl get ingress sdlc-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending...")
INGRESS_HOST=$(kubectl get ingress sdlc-ingress -n ${NAMESPACE} -o jsonpath='{.spec.rules[0].host}' 2>/dev/null || echo "Not configured")

echo "Ingress Host: ${INGRESS_HOST}"
echo "Ingress IP: ${INGRESS_IP}"

# Show pod status
echo ""
echo "Pod Status:"
kubectl get pods -n ${NAMESPACE} -o wide

# Show service status
echo ""
echo "Service Status:"
kubectl get services -n ${NAMESPACE}

# Show ingress status
echo ""
echo "Ingress Status:"
kubectl get ingress -n ${NAMESPACE}

# Health check
echo ""
echo "🏥 Running health checks..."

# Wait a bit for services to stabilize
sleep 30

# Check backend health
BACKEND_POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ ! -z "${BACKEND_POD}" ]; then
    if kubectl exec -n ${NAMESPACE} ${BACKEND_POD} -- curl -f http://localhost:5000/api/health &>/dev/null; then
        echo "✅ Backend health check passed"
    else
        echo "❌ Backend health check failed"
    fi
fi

# Check frontend health
FRONTEND_POD=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ ! -z "${FRONTEND_POD}" ]; then
    if kubectl exec -n ${NAMESPACE} ${FRONTEND_POD} -- curl -f http://localhost:80/health &>/dev/null; then
        echo "✅ Frontend health check passed"
    else
        echo "❌ Frontend health check failed"
    fi
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Access your SDLC Platform at:"
if [ "${INGRESS_HOST}" != "Not configured" ]; then
    echo "🌐 https://${INGRESS_HOST}"
else
    echo "🌐 Configure your DNS to point to: ${INGRESS_IP}"
fi
echo ""
echo "Monitoring Dashboard:"
echo "📊 Grafana: https://${INGRESS_HOST}/grafana"
echo "📈 Prometheus: https://${INGRESS_HOST}/prometheus"
echo ""
echo "To get logs:"
echo "kubectl logs -f deployment/sdlc-backend -n ${NAMESPACE}"
echo "kubectl logs -f deployment/sdlc-frontend -n ${NAMESPACE}"
echo ""
echo "To uninstall:"
echo "helm uninstall ${RELEASE_NAME} -n ${NAMESPACE}"