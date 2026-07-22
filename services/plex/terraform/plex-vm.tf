resource "proxmox_virtual_environment_vm" "plex" {
  name      = "plex"
  node_name = "ilab-node-02"
  vm_id     = 102
  
  # Set to q35 and ovmf as identified in plan
  machine       = "q35"
  bios          = "ovmf"
  scsi_hardware = "virtio-scsi-single"

  cpu {
    cores = 4
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = 6144
  }

  network_device {
    bridge   = "vmbr0"
    firewall = true
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 50
    file_format  = "raw"
    discard      = "on"
    iothread     = true
    replicate    = false
  }

  efi_disk {
    datastore_id      = "vmstore"
    file_format       = "raw"
    type              = "4m"
    pre_enrolled_keys = true # CRITICAL: This prevents the 'destroy/replace' action
  }

  agent {
    enabled = true
    timeout = "15m"
    type    = "virtio"
  }

  # Standard lifecycle for lab stability
  lifecycle {
    ignore_changes = [
      initialization,
    ]
  }
}