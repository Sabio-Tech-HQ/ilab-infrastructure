resource "proxmox_virtual_environment_vm" "haproxy_cluster" {
  count     = 2
  # This sets the name in the Proxmox UI
  name      = "haproxy-0${count.index + 1}"
  node_name = "ilab-node-03" 

  clone {
    vm_id = 1009 
  }

  initialization {
    datastore_id = "vmstore"
    
    # The hostname is often inherited from the 'name' field above in newer providers,
    # but we must ensure the IP configuration is unique.
    ip_config {
      ipv4 {
        address = "10.10.10.${204 + count.index}/24"
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

  # REMOVE ignore_changes so Terraform can actually fix the identity
  # lifecycle {
  #   ignore_changes = [initialization]
  # }
}