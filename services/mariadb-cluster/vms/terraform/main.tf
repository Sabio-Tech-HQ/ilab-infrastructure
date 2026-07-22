# --- 1. Create MariaDB VMs

resource "proxmox_virtual_environment_vm" "mariadb_cluster" {
  for_each = {
    "01" = { vid = 109, ip = "10.10.10.41/24" }
    "02" = { vid = 123, ip = "10.10.10.42/24" }
    "03" = { vid = 124, ip = "10.10.10.43/24" }
  }

  name      = "mariadb-${each.key}"
  node_name = "ilab-node-03"
  vm_id     = each.value.vid
  bios      = "seabios"

  clone {
    vm_id = 1009
  }

  scsi_hardware = "virtio-scsi-single"

  cpu {
    type  = "x86-64-v2-AES"
    cores = 2
  }

  memory {
    dedicated = 3072
  }

  agent {
    enabled = false
  }

  # Prevents Proxmox provider from querying the QEMU agent for network data
  lifecycle {
    ignore_changes = [
      network_interface_names,
      ipv4_addresses,
      ipv6_addresses,
    ]
  }

  network_device {
    bridge = "vmbr0"
  }

  operating_system {
    type = "l26"
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 30
    file_format  = "raw"
    iothread     = true
    discard      = "on"
  }

  initialization {
    ip_config {
      ipv4 {
        address = each.value.ip
        gateway = "10.10.10.1"
      }
    }
    user_account {
      username = var.ssh_user
      password = var.ssh_password
      keys     = var.ssh_public_keys
    }
  }
}


# --- 2. Create MaxScale VMs

resource "proxmox_virtual_environment_vm" "maxscale_cluster" {
  for_each = {
    "01" = { vid = 125, ip = "10.10.10.46/24" }
    "02" = { vid = 126, ip = "10.10.10.47/24" }
  }

  name      = "maxscale-${each.key}"
  node_name = "ilab-node-03"
  vm_id     = each.value.vid
  bios      = "seabios"

  clone {
    vm_id = 1009
  }

  scsi_hardware = "virtio-scsi-single"

  cpu {
    type  = "x86-64-v2-AES"
    cores = 2
  }

  memory {
    # MaxScale is just routing traffic, it doesn't need as much RAM as the DBs
    dedicated = 2048 
  }

  agent {
    enabled = false
  }

  # Prevents Proxmox provider from querying the QEMU agent for network data
  lifecycle {
    ignore_changes = [
      network_interface_names,
      ipv4_addresses,
      ipv6_addresses,
    ]
  }

  network_device {
    bridge = "vmbr0"
  }

  operating_system {
    type = "l26"
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 20 # 20GB is plenty for the proxy OS
    file_format  = "raw"
    iothread     = true
    discard      = "on"
  }

  initialization {
    ip_config {
      ipv4 {
        address = each.value.ip
        gateway = "10.10.10.1"
      }
    }
    user_account {
      username = var.ssh_user
      password = var.ssh_password
      keys     = var.ssh_public_keys
    }
  }
}