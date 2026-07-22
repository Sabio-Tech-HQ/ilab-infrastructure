resource "proxmox_virtual_environment_vm" "pihole" {
  count     = 3
  name      = "pihole-0${count.index + 1}"
  node_name = "pve"
  vm_id     = 100 + count.index # Optional: explicitly map VMIDs

  initialization {
    ip_config {
      ipv4 {
        address = "10.10.10.1${count.index}/24"
        gateway = "10.10.10.1"
      }
    }
    user_account {
      keys = [var.ssh_public_key]
    }
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 1024
  }

  network_device {
    bridge = "vmbr0"
  }
}