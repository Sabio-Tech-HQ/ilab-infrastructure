resource "proxmox_virtual_environment_vm" "jellyfin" {
  name      = "jellyfin"
  node_name = "ilab-node-03"
  vm_id     = 104
  
  # Set to q35 and ovmf as identified in plan
  machine       = "q35"
  bios          = "ovmf"
  scsi_hardware = "virtio-scsi-single"

  cpu {
    cores = 4
    sockets = 1
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
    size         = 40
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


  initialization {
    user_account {
      username = var.ssh_user
      keys     = split(", ", var.ssh_public_key)
    }
  }

  # THIS IS THE META-ARGUMENT BLOCK
  lifecycle {
    ignore_changes = [
      initialization, # This tells Terraform: "Don't try to change Cloud-init after the VM is built"
    ]
  }
  
}