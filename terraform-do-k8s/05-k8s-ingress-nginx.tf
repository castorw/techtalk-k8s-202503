resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  namespace  = "kube-system"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  version    = "4.12.0"
}
