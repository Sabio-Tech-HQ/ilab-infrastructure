output "media_vm_ip" {
  # 1. Changed "media_vm" to "media"
  # 2. Added [0] right after media because "count = 1" makes it a list
  value       = proxmox_virtual_environment_vm.media[0].ipv4_addresses[1][0]
  description = "The primary IP address of the Media VM"
}