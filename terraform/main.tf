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

# Secrets Manager for DB
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

resource "random_password" "db_password" {
  length           = 16
  override_special = "!@#$%&*()-_=+[]{}<>?"
  special          = true
}

# RDS PostgreSQL
resource "aws_db_instance" "authdb" {
  allocated_storage    = var.db_storage
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = var.db_instance_class
  db_name                 = var.db_name
  username             = var.db_username
  password             = random_password.db_password.result
  skip_final_snapshot  = true
  multi_az             = var.db_multi_az
  publicly_accessible  = false
}

resource "kubernetes_namespace" "auth_prod" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_service_account" "auth_sa" {
  metadata {
    name      = "auth-sa"
    namespace = kubernetes_namespace.auth_prod.metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = var.iam_role_arn
    }
  }
}

resource "kubernetes_deployment" "auth" {
  metadata {
    name      = "auth-deployment"
    namespace = kubernetes_namespace.auth_prod.metadata[0].name
    labels = { app = "auth-service" }
  }

  spec {
    replicas = var.app_replicas

    selector {
      match_labels = { app = "auth-service" }
    }

    template {
      metadata { labels = { app = "auth-service" } }

      spec {
        service_account_name = kubernetes_service_account.auth_sa.metadata[0].name

        container {
          name  = "auth-container"
          image = var.app_image

          port { container_port = var.app_port }

          env {
            name  = "ENVIRONMENT"
            value = "production"
          }
          env {
            name  = "AWS_REGION"
            value = var.aws_region
          }
          env {
            name  = "AWS_SECRET_NAME"
            value = var.aws_secret_name
          }

          readiness_probe{
            http_get {
             path = "/health"
             port = var.app_port 
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }

          liveness_probe{
            http_get { 
                path = "/health"
                port = var.app_port 
            }
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

resource "kubernetes_service" "auth" {
  metadata {
    name      = "auth-service"
    namespace = kubernetes_namespace.auth_prod.metadata[0].name
    labels    = { app = "auth-service" }
  }

  spec {
    selector = { app = "auth-service" }

    port {
      name        = "metrics"
      port        = 80
      target_port = var.app_port
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }
}
