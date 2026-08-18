resource "proxmox_virtual_environment_vm" "vaultwarden_cluster" {
  count     = 3
  name      = "vaultwarden-0${count.index + 1}"
  node_name = "ilab-node-03" 

  # Enable the QEMU guest agent now that it's installed in the guest
  agent {
    enabled = true
  }

  clone {
    vm_id = 1009 
  }

  initialization {
    datastore_id = "vmstore"

    ip_config {
      ipv4 {
        address = "10.10.10.${207 + count.index}/24"
        gateway = "10.10.10.1"
      }
    }

    user_account {
      username = var.ssh_user
      keys     = [
        var.ssh_public_key,
        file("/home/jthairu/.ssh/id_ed25519.pub")
      ]
      password = var.ssh_password  
    }
  }

  lifecycle {
    ignore_changes = [
      node_name,
      initialization,
      network_device[0].mac_address,
      clone
    ]
  }
}