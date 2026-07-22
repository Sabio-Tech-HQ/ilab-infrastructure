output "media_vm_ip" {
  value       = proxmox_virtual_environment_vm.media_vm.ipv4_addresses[1][0]
  description = "The primary IP address of the Media VM"
}