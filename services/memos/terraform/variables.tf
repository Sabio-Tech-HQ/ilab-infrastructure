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

variable "ssh_public_key" {
  description = "The public SSH key to be injected into the instances"
  type        = string
}

variable "ssh_public_keys" {
  description = "List of SSH public keys (defined in tfvars)"
  type        = string 
  default     = ""
}

variable "ssh_password" {
  description = "SSH password for the instances"
  type        = string
  sensitive   = true
  default     = ""
}

variable "target_node" {
  description = "The Proxmox node where the VM/LXC will be installed (e.g., ilab-node-01)"
  type        = string
}

variable "node_template_map" {
  description = "Map of Proxmox nodes to their specific template IDs"
  type        = map(number)
  default     = {
    "ilab-node-01" = 1001
    "ilab-node-02" = 1002
    "ilab-node-03" = 1003
  }
}

variable "ssh_user" { 
  type    = string
  default = null 
}

variable "cloud_init_image_id" { 
  type    = string
  default = null 
}

variable "lxc_template_id" {
  type    = string
  default = null
}

# Added for Memos LXC provisioning
variable "memos_ip" {
  description = "The static IP for the Memos LXC"
  type        = string
  default     = "10.10.10.35"
}

variable "memos_user" {
  description = "The username for the Memos LXC"
  type        = string
  default     = "jthairu"
}