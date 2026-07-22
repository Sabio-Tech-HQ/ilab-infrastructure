terraform {
  required_providers {
    mysql = {
      source  = "petoju/mysql"
      version = "~> 3.0"
    }
  }
}

provider "mysql" {
  endpoint = "10.10.10.41:3306"
  username = "root"
  password = var.mysql_root_password
}