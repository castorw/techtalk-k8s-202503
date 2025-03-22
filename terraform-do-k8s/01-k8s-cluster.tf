resource "digitalocean_kubernetes_cluster" "cluster" {
  name                             = local.k8s_cluster_name
  region                           = "fra1"
  version                          = "1.32.2-do.0"
  auto_upgrade                     = false
  destroy_all_associated_resources = true
  kubeconfig_expire_seconds        = 315360000

  node_pool {
    name       = "${local.k8s_cluster_name}-pool-1"
    size       = "s-1vcpu-2gb"
    node_count = 3
  }

  timeouts {
    create = "60m"
  }
}
