

variable "ssh_password" {
  type        = string
  sensitive   = true
  description = "SSH password"
}


variable "ssh_public_keys" {
  description = "The public SSH key to be injected into the VMs"
  type    = list(string)
  default = []
}

variable "ssh_public_key" {
  description = "The public SSH key to be injected into the VMs"
  type        = string
}

variable "ssh_user" {
  type    =   string   
}

variable "pacs_password" {
  description = "Password for the PACS MySQL user"
  type        = string
  sensitive   = true
}

variable "mysql_root_password" {
  description = "Password for mysql root"
  type        = string
  sensitive   = true
}



variable "proxmox_api_url" {
  type = string
}

variable "proxmox_api_token_id" {
  type = string
}

variable "proxmox_api_token_secret" {
  type      = string
  sensitive = true
}
