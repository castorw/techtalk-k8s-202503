resource "digitalocean_domain" "app_domain" {
  name = local.app_domain
}

resource "kubernetes_secret" "external_dns_digitalocean" {
  metadata {
    name      = "digital-ocean-dns"
    namespace = "kube-system"
  }
  data = {
    token = var.external_dns_digitalocean_token
  }
}

resource "helm_release" "external_dns" {
  name       = "external-dns"
  namespace  = "kube-system"
  repository = "https://kubernetes-sigs.github.io/external-dns/"
  chart      = "external-dns"
  version    = "1.16.0"
  values = [yamlencode({
    domainFilters = [local.app_domain]
    provider = {
      name = "digitalocean"
    }
    env = [
      {
        name = "DO_TOKEN"
        valueFrom = {
          secretKeyRef = {
            name = kubernetes_secret.external_dns_digitalocean.metadata.0.name
            key  = "token"
          }
        }
      }
    ]
  })]
}
