resource "proxmox_virtual_environment_vm" "traefik_vms" {
  for_each = {
    "traefik-01" = { id = 113, ip = "10.10.10.16", node = "ilab-node-03" }
    "traefik-02" = { id = 105, ip = "10.10.10.17", node = "ilab-node-02" }
    "traefik-03" = { id = 114, ip = "10.10.10.18", node = "ilab-node-02" }
  }

  name      = each.key
  vm_id     = each.value.id
  node_name = each.value.node
  bios      = "ovmf"

  cpu {
    cores = 2
    type  = "host"
  }

  memory {
    dedicated = 2048
  }

  efi_disk {
    datastore_id      = "vmstore"
    pre_enrolled_keys = true
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 20
  }

  network_device {
    bridge = "vmbr0"
    model  = "virtio"
  }

  initialization {
    datastore_id = "vmstore"
    
    ip_config {
      ipv4 {
        address = "${each.value.ip}/24"
        gateway = "10.10.10.1"
      }
    }

    user_account {
      keys     = [var.ssh_public_key]
      username = "jamesthairu"
    }
  }

  lifecycle {
    # This prevents the 'Destroy/Recreate' behavior you just saw
    ignore_changes = [
      disk,
      network_device,
      efi_disk,
      initialization[0].user_account
    ]
  }
}