variable "k8s_cluster_name" {
  type = string
}

variable "domain" {
  type = string
}

variable "external_dns_digitalocean_token" {
  type = string
}

variable "cert_manager_letsencrypt_email" {
  type = string
}
