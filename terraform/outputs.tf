output "db_endpoint" {
  value = aws_db_instance.authdb.address
}

output "db_secret_arn" {
  value = aws_secretsmanager_secret.db_secret.arn
}
