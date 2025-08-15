variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "eks_cluster_name" {
  type    = string
  default = "metalcloud-cluster"
}

variable "namespace" {
  type    = string
  default = "auth-prod"
}

variable "iam_role_arn" {
  type = string
}

variable "aws_secret_name" {
  type = string
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_name" {
  type    = string
  default = "authdb_prod"
}

variable "db_storage" {
  type    = number
  default = 20
}

variable "db_multi_az" {
  type    = bool
  default = false
}

variable "db_username" {
  type    = string
  default = "authuser"
}

variable "db_password" {
  type    = string
  default = "" # Lo generaremos automáticamente en Secrets Manager si está vacío
}

variable "app_image" {
  type    = string
  default = "gilbr/auth-service:latest"
}

variable "app_replicas" {
  type    = number
  default = 1
}

variable "app_port" {
  type    = number
  default = 8000
}
