terraform {
  required_providers {
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "1.25.0"
    }
  }
}

provider "postgresql" {
  host            = "10.10.10.200"
  port            = 5432
  database        = "postgres"
  username        = "postgres"
  password        = var.db_password
  sslmode         = "disable"
}