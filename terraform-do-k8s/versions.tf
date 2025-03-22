terraform {
  backend "local" {}

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "2.49.2"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.36.0"
    }
    kubectl = {
      source  = "alekc/kubectl"
      version = "2.1.3"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "3.0.0-pre2"
    }
  }
}
