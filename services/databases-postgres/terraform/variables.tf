variable "db_vip" {
  type        = string
  description = "The Floating VIP pointing to HAProxy"
}

variable "db_password" {
  type        = string
  sensitive   = true
}

variable "media_dbs_password" {
  type        = string
  sensitive   = true
}



variable "app_db_passwords" {
  type        = map(string)
  description = "Map of passwords for pacs, airflow, vitals"
  sensitive   = true
}