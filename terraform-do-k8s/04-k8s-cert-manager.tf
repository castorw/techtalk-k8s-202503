resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  namespace  = "kube-system"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  version    = "1.17.1"
  values = [yamlencode({
    namespace   = "kube-system"
    installCRDs = true
  })]
}

resource "kubectl_manifest" "cert_manager_issuer" {
  depends_on = [helm_release.cert_manager]
  yaml_body = yamlencode({
    apiVersion = "cert-manager.io/v1"
    kind       = "ClusterIssuer"
    metadata = {
      name = "letsencrypt-dns01"
    }
    spec = {
      acme = {
        server = "https://acme-v02.api.letsencrypt.org/directory"
        email  = var.cert_manager_letsencrypt_email
        privateKeySecretRef = {
          name = "letsencrypt-dns01-private"
        }
        solvers = [
          {
            dns01 = {
              digitalocean = {
                tokenSecretRef = {
                  name = kubernetes_secret.external_dns_digitalocean.metadata.0.name
                  key  = "token"
                }
              }
            }
          }
        ]
      }
    }
  })
}
