terraform {
  required_providers {
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "1.25.0"
    }
  }
}

provider "postgresql" {
  host            = var.db_vip
  port            = 5432
  username        = "terraform" 
  password        = var.db_password
  sslmode         = "disable"
  connect_timeout = 15
}