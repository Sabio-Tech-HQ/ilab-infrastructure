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


variable "ssh_public_keys" {
  type = list(string)
}

variable "ssh_password" {
  description = "SSH password for the instances"
  type        = string
  sensitive   = true
  default     = ""
}

variable "ssh_user" { 
  type    = string
  default = "jthairu"
}

variable "cloud_init_image_id" { 
  type    = string
  default = null 
}

variable "lxc_template_id" {
  type    = string
  default = null
}

# Added for Penpot LXC provisioning
variable "pngx_ip" {
  description = "The static IP for the Memos LXC"
  type        = string
  default     = "10.10.10.94"
}
