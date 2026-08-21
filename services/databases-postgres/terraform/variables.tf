variable "db_vip" {
  type        = string
  description = "The Floating VIP pointing to HAProxy"
}

variable "db_password" {
  type        = string
  sensitive   = true
}



variable "vaultwarden_db_password" {
  type      = string
  sensitive = true
}

variable "penpot_db_password" {
  description = "Password for the Penpot PostgreSQL user"
  type        = string
  sensitive   = true
}