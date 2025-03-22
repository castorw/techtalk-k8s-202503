resource "helm_release" "argocd" {
  name             = "argocd"
  namespace        = "argocd"
  create_namespace = true
  repository       = "oci://ghcr.io/argoproj/argo-helm"
  chart            = "argo-cd"
  version          = "7.8.13"
  values = [yamlencode(({
    server = {
      ingress = {
        enabled          = true
        ingressClassName = "nginx"
        hostname         = "argocd.${var.domain}"
        tls              = true
        annotations = {
          "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
          "cert-manager.io/cluster-issuer"                 = kubectl_manifest.cert_manager_issuer.name
        }
      }
    }
    configs = {
      params = {
        "server.insecure" = true
      }
    }
  }))]
}

data "kubernetes_secret" "argocd_initial_admin_secret" {
  metadata {
    name      = "argocd-initial-admin-secret"
    namespace = helm_release.argocd.metadata.namespace
  }
}

output "argocd_password" {
  sensitive = false
  value     = nonsensitive(data.kubernetes_secret.argocd_initial_admin_secret.data.password)
}
