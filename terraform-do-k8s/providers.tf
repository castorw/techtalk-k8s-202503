provider "digitalocean" {}

provider "kubernetes" {
  host                   = digitalocean_kubernetes_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(digitalocean_kubernetes_cluster.cluster.kube_config.0.cluster_ca_certificate)
  client_certificate     = digitalocean_kubernetes_cluster.cluster.kube_config.0.client_certificate
  client_key             = digitalocean_kubernetes_cluster.cluster.kube_config.0.client_key
  token                  = digitalocean_kubernetes_cluster.cluster.kube_config.0.token
}

provider "helm" {
  kubernetes = {
    host                   = digitalocean_kubernetes_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(digitalocean_kubernetes_cluster.cluster.kube_config.0.cluster_ca_certificate)
    client_certificate     = digitalocean_kubernetes_cluster.cluster.kube_config.0.client_certificate
    client_key             = digitalocean_kubernetes_cluster.cluster.kube_config.0.client_key
    token                  = digitalocean_kubernetes_cluster.cluster.kube_config.0.token
  }
}

provider "kubectl" {
  host                   = digitalocean_kubernetes_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(digitalocean_kubernetes_cluster.cluster.kube_config.0.cluster_ca_certificate)
  client_certificate     = digitalocean_kubernetes_cluster.cluster.kube_config.0.client_certificate
  client_key             = digitalocean_kubernetes_cluster.cluster.kube_config.0.client_key
  token                  = digitalocean_kubernetes_cluster.cluster.kube_config.0.token
}
