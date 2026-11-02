variable "proxmox_api_url" { type = string }
variable "proxmox_api_token_id" { type = string }
variable "proxmox_api_token_secret" {
  type      = string
  sensitive = true
}
variable "ssh_public_key" { type = string }
variable "ssh_password" {
  type      = string
  sensitive = true
}
variable "immich_ip" {
  type    = string
  default = "10.10.10.93"
}
