resource "proxmox_virtual_environment_vm" "kafka_cluster" {
  count = 3
  name      = "kafka-0${count.index + 1}"
  node_name = "ilab-node-03"

  clone {
    vm_id = 1003 
  }

  # Hardware configuration for q35/ovmf compatibility
  machine       = "q35"
  bios          = "ovmf"
  scsi_hardware = "virtio-scsi-single"

  cpu {
    cores = 4
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = 8192
  }

  network_device {
    bridge   = "vmbr0"
    firewall = false
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 60
    file_format  = "raw"
    discard      = "on"
    iothread     = true
    replicate    = false
  }

  efi_disk {
    datastore_id      = "vmstore"
    file_format       = "raw"
    type              = "4m"
    pre_enrolled_keys = true 
  }

  agent {
    enabled = true
    timeout = "15m"
    type    = "virtio"
  }

  initialization {
    # Storage location for the Cloud-Init configuration drive
    datastore_id = "vmstore" 
    
    ip_config {
      ipv4 {
        # This will result in 10.10.10.235, .236, and .237
        address = "10.10.10.${235 + count.index}/24"
        gateway = "10.10.10.1"
      }
    }
    
    user_account {
      username = var.ssh_user
      keys     = split(", ", var.ssh_public_key)
    }
  }

  lifecycle {
    ignore_changes = [
      initialization,
    ]
  }
}