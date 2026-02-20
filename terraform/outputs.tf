output "ecr_repository_url" {
  value = aws_ecr_repository.frontend.repository_url
}

output "cluster_name" {
  value = aws_ecs_cluster.this.name
}
