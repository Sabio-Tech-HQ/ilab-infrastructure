variable "proxmox_api_url" {
  type        = string
  description = "Proxmox API endpoint URL"
}

variable "proxmox_api_token_id" {
  type        = string
  description = "Proxmox API token ID (e.g., user@pam!tokenname)"
}

variable "proxmox_api_token_secret" {
  type        = string
  description = "Proxmox API token secret UUID"
  sensitive   = true
}

variable "ittools_ip" {
  type        = string
  description = "Static IP address for the Ollama LXC container"
  default     = "10.10.10.119"
}

variable "ssh_public_keys" {
  description = "The public SSH key to be injected into the VMs"
  type    = list(string)
  default = []
}

variable "ssh_password" {
  type        = string
  description = "Default root/user password"
  sensitive   = true
}