# The Storage Gateway (The "4th VM")
resource "proxmox_virtual_environment_vm" "storage_node" {
  name      = "oracle-storage-gw"
  node_name = "ilab-node-03" 
  vm_id     = 144 

  clone {
    vm_id = 1003
    full  = true
  } 

  network_device { bridge = "vmbr0" } 
  network_device { bridge = "vmbr1" } 

  # DISK 1: The OS (sda) 
  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
     size         = 32
  }

  # DISK 2: The Shared Storage (sdb) - shared with db nodes
  disk {
    datastore_id = "vmstore"
    interface    = "scsi1" 
    size         = 80
    file_format  = "raw"
    cache        = "none"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "10.10.10.144/24"
        gateway = "10.10.10.1"
      }
    }
    ip_config {
      ipv4 {
        address = "10.10.20.144/24"
      }
    }
    user_account {
      username = var.ssh_user
      password = var.ssh_password
      keys     = split(", ", var.ssh_public_key)
    }
  }
}

# 3 Oracle Database Nodes (Sequential: 141, 142, 143)
resource "proxmox_virtual_environment_vm" "oracle_nodes" {
  count     = 3
  name      = "oracle-node-0${count.index + 1}"
  node_name = "ilab-node-03"
  vm_id     = 141 + count.index  

  clone {
    vm_id = 1003
    full  = true
  } 

  cpu { cores = 2 }
  memory { dedicated = 4096 }

  network_device { bridge = "vmbr0" }
  network_device { bridge = "vmbr1" } 

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 40 
    file_format  = "raw"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "10.10.10.${141 + count.index}/24" 
        gateway = "10.10.10.1"
      }
    }
    ip_config {
      ipv4 {
        address = "10.10.20.${141 + count.index}/24" # Fixed index to match
      }
    }
    user_account {
      username = var.ssh_user
      password = var.ssh_password
      keys     = split(", ", var.ssh_public_key)
    }
  }
}