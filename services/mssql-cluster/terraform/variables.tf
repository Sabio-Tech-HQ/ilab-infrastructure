variable "proxmox_api_url" {
  type    = string
  default = "https://10.10.10.103:8006/api2/json" 
}

variable "proxmox_api_token_id" {
  type      = string
  sensitive = true
}

variable "proxmox_api_token_secret" {
  type      = string
  sensitive = true
}

variable "template_name" {
  type    = string
  default = "winserver2022-template-03"
}

variable "network_gateway" {
  type    = string
  default = "10.10.10.1"
}

variable "domain_admin_password" {
  type      = string
  sensitive = true
}