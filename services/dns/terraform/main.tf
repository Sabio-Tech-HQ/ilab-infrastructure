resource "proxmox_virtual_environment_vm" "pihole" {
  count     = 3
  name      = "pihole-0${count.index + 1}"
  node_name = ["ilab-node-02", "ilab-node-02", "ilab-node-03"][count.index]
  vm_id     = [103, 115, 116][count.index]

  # Hardware Specs to match your "Refreshing State"
  machine       = "q35"
  bios          = "ovmf"
  scsi_hardware = "virtio-scsi-single"

  agent {
    enabled = true
    timeout = "15m"
    type    = "virtio"
  }

  cpu {
    cores = 2
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = 1024
  }

  network_device {
    bridge   = "vmbr0"
    firewall = true
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 25
    file_format  = "raw"
    discard      = "on"
    iothread     = true
  }

  efi_disk {
    datastore_id      = "vmstore"
    file_format       = "raw"
    type              = "4m"
    pre_enrolled_keys = true
  }

  initialization {
    ip_config {
      ipv4 {
        # Using the IPs identified in your previous plan
        address = ["10.10.10.10/24", "10.10.10.11/24", "10.10.10.13/24"][count.index]
        gateway = "10.10.10.1"
      }
    }
    user_account {
      keys = [var.ssh_public_key]
    }
  }

  # THE SAFETY NET
  # This prevents the "Destroy/Create" loop for existing VMs
  lifecycle {
    ignore_changes = [
      initialization,
      network_device[0].mac_address,
    ]
  }
}