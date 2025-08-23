# -----------------------------------------------------------------------------
# Template created by GitHub: https://github.com/MetalCloud1
# Licensed under CC BY-NC-ND (custom) – see LICENSE.md for details
# Free to use for personal, work, educational, or inspiration purposes with prior notice
# -----------------------------------------------------------------------------
provider "aws" {
  region = var.aws_region
}

data "aws_eks_cluster" "eks" {
  name = var.eks_cluster_name
}

data "aws_eks_cluster_auth" "eks" {
  name = var.eks_cluster_name
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.eks.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.eks.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.eks.token
}

resource "random_password" "db_password" {
  length           = 16
  override_special = "!@#$%&*()-_=+[]{}<>?"
  special          = true
}

resource "aws_secretsmanager_secret" "db_secret" {
  name = var.aws_secret_name
}

resource "aws_secretsmanager_secret_version" "db_secret_version" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    db_name  = var.db_name
  })
}

resource "aws_db_instance" "authdb" {
  allocated_storage    = var.db_storage
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = var.db_instance_class
  db_name              = var.db_name
  username             = var.db_username
  password             = random_password.db_password.result
  skip_final_snapshot  = true
  multi_az             = var.db_multi_az
  publicly_accessible  = false
}

variable "services" {
  type = list(object({
    name     = string
    image    = string
    port     = number
    replicas = number
  }))
  default = [
    { name = "auth-service", image = var.app_image, port = var.app_port, replicas = var.app_replicas },
    { name = "users-api",  image = "gilbr/users-api:latest", port = 8000, replicas = 1 }
  ]
}

resource "kubernetes_namespace" "services" {
  for_each = { for s in var.services : s.name => s }
  metadata {
    name = each.value.name
  }
}

resource "kubernetes_deployment" "services" {
  for_each = { for s in var.services : s.name => s }

  metadata {
    name      = "${each.value.name}-deployment"
    namespace = each.value.name
    labels    = { app = each.value.name }
  }

  spec {
    replicas = each.value.replicas

    selector {
      match_labels = { app = each.value.name }
    }

    template {
      metadata { labels = { app = each.value.name } }

      spec {
        container {
          name  = each.value.name
          image = each.value.image

          port { container_port = each.value.port }

          readiness_probe {
            http_get { path = "/health"; port = each.value.port }
            initial_delay_seconds = 5
            period_seconds        = 10
          }

          liveness_probe {
            http_get { path = "/health"; port = each.value.port }
            initial_delay_seconds = 15
            period_seconds        = 20
          }

          resources {
            limits   = { cpu = "250m", memory = "512Mi" }
            requests = { cpu = "125m", memory = "256Mi" }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "services" {
  for_each = { for s in var.services : s.name => s }

  metadata {
    name      = "${each.value.name}-service"
    namespace = each.value.name
    labels    = { app = each.value.name }
  }

  spec {
    selector = { app = each.value.name }

    port {
      name        = "http"
      port        = 80
      target_port = each.value.port
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}

# Monitoring Stack (Helm)

resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
}

resource "helm_release" "loki" {
  name       = "loki"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "loki-stack"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
}

resource "helm_release" "grafana" {
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name

  values = [
    file("grafana-values.yaml")
  ]
}
