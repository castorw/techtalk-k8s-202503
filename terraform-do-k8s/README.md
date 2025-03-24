# Sample Terraform Module
This Terraform module deploys a full-featured managed **Kubernetes cluster in DigitalOcean**, installs required components and launches the sample application using ArgoCD.

## Setup
To fully deploy this sample it is required that you own a domain and can delegate a subdomain for DigitalOcean. For example, if your domain is `example.com`, then you can create the following NS records to forward a subdomain named `k8s.example.com`:
>
```
k8s.example.com.    NS    IN    ns1.digitalocean.com.
k8s.example.com.    NS    IN    ns2.digitalocean.com.
k8s.example.com.    NS    IN    ns3.digitalocean.com.
```

To use this Terraform module it is necessary to do the following:
1. Create DigitalOcean account (https://cloud.digitalocean.com),
2. Create a full-access DigitalOcean API token and place it in your environment file in variable named `DIGITALOCEAN_TOKEN`,
3. Create a limited-access token with full `Domain` scope access (`create`, `read`, `update`, `delete`),
4. Create a domain or subdomain pointing to DigitalOcean DNS servers as described above,
5. Create a file named `config.auto.tfvars` in this folder with the following contents:
```
k8s_cluster_name                = "k8s-cluster-1"
domain                          = "k8s-cluster-1.example.con"
external_dns_digitalocean_token = "dop_v1_............."
cert_manager_letsencrypt_email  = "your.email@example.com"
```

Update all of the variables according to your preference. Fill in the token from step 3 to `external_dns_digitalocean_token`.

## Contents
This module contains resource to fulfill create the following resources:
| File | Description |
| - | - |
| `versions.tf` | Defines Terraform backend and required providers with their respective versions. |
| `variables.tf` | Defines input variables that must be provided to the module (the `config.auto.tfvars` file does this for us). |
| `providers.tf` | Defines provider configuration. DigitalOcean provider runs in default settings. Kubernetes, Kubectl Manifest and Helm providers use credentials from created Kubernetes cluster provided by DigitalOcean. |
| `01-k8s-cluster.tf` | Provisions a Kubernetes cluster in DigitalOcean. |
| `02-k8s-metrics-server.tf` | Installs `metrics-server` in Kubernetes cluster using Helm provider. |
| `03-k8s-dns.tf` | Provisions domain in DigitalOcean and installs External DNS controller using Helm provider. |
| `04-k8s-cert-manager.tf` | Installs `cert-manager` using Helm provider and configures Letsencrypt issuer with DNS-01 verification. |
| `05-k8s-ingress-nginx.tf` | Installs `ingress-nginx` using Helm provider. |
| `06-k8s-argocd.tf` | Installs ArgoCD using Helm provider. |
| `10-argocd-my-app.tf` | Deploys our sample app `my-app` using ArgoCD Application utilising our sample Helm chart. Deployment-specific values are included in this file. |
