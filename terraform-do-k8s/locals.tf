locals {
  k8s_cluster_name = "tt-k8s-cluster-1"
  app_domain       = "${local.k8s_cluster_name}.ctrdn.net"
}
