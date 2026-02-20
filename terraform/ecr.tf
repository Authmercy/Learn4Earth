resource "aws_ecr_repository" "frontend" {
  name = "react-frontend"

  image_scanning_configuration {
    scan_on_push = true
  }
}
