resource "kubectl_manifest" "argocd_my_app_application" {
  depends_on = [helm_release.argocd]
  yaml_body = yamlencode({
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    metadata = {
      name      = "my-app"
      namespace = "argocd"
    }
    spec = {
      project = "default"
      source = {
        repoURL        = "https://github.com/castorw/techtalk-k8s-202503.git"
        path           = "my-app/chart"
        targetRevision = "main"
        helm = {
          valuesObject = {
            server = {
              ingress = {
                enabled   = true
                className = "nginx"
                annotations = {
                  "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
                  "cert-manager.io/cluster-issuer"                 = kubectl_manifest.cert_manager_issuer.name
                  "nginx.ingress.kubernetes.io/proxy-body-size"    = "1g"
                  "nginx.ingress.kubernetes.io/proxy-read-timeout" = "300"
                  "nginx.ingress.kubernetes.io/proxy-send-timeout" = "300"
                }
                hostname = "my-app.${var.domain}"
                tls      = true
              }
            }
            postgresql = {
              primary = {
                persistence = {
                  storageClass = "do-block-storage"
                }
              }
            }
            redis = {
              master = {
                persistence = {
                  storageClass = "do-block-storage"
                }
              }
            }
          }
        }
      }
      destination = {
        name      = "in-cluster"
        namespace = "my-app-prod"
      }
      syncPolicy = {
        automated = {
          prune      = true
          allowEmpty = true
        }
        syncOptions = [
          "CreateNamespace=true"
        ]
      }
    }
  })
}
