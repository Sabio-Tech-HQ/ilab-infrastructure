resource "proxmox_virtual_environment_vm" "nebula_sync" {
  name      = "nebula-sync"
  node_name = "ilab-node-01" 
  vm_id     = 117
  bios      = "ovmf"
  machine   = "q35"

  efi_disk {
    datastore_id      = "vmstore"
    file_format       = "raw"
    pre_enrolled_keys = true
    type              = "4m"
  }

  scsi_hardware = "virtio-scsi-single"

  cpu {
    type    = "x86-64-v2-AES"
    cores   = 2
    sockets = 1
  }

  memory {
    dedicated = 2048 
  }

  agent {
    enabled = true
  }

  network_device {
    bridge   = "vmbr0"
    firewall = true
  }

  operating_system {
    type = "l26"
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 10 
    file_format  = "raw"
    iothread     = true
    discard      = "on"
  }

  lifecycle {
    ignore_changes = [
      node_name,
      initialization,
      network_device[0].mac_address,
      clone,
      efi_disk,
    ]
  }
}