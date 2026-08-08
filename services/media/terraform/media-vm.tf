resource "proxmox_virtual_environment_vm" "media" {
  count     = 1
  name      = "media"
  node_name = "ilab-node-03"
  vm_id     = 101
  
  bios          = "ovmf"
  machine       = "q35"
  scsi_hardware = "virtio-scsi-single"

  agent {
    enabled = true
  }

  cpu {
    cores   = 4
    sockets = 1
    type    = "x86-64-v2-AES"
  }

  memory {
    dedicated = 8192
  }

  efi_disk {
    datastore_id      = "vmstore"
    file_format       = "raw"
    pre_enrolled_keys = true
    type              = "4m"
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 45
    file_format  = "raw"
    iothread     = true
    discard      = "on"
  }

  network_device {
    bridge      = "vmbr0"
    mac_address = "BC:24:11:7B:C2:08" # Keeps your existing MAC address
  }

  operating_system {
    type = "l26"
  }

  initialization {
    ip_config {
      ipv4 {
        address = "10.10.10.30/24"
        gateway = "10.10.10.1"
      }
    }
    # Removed the user_account block because injecting new SSH keys 
    # into an existing VM via Terraform forces a total VM replacement.
  }

  # This tells Terraform to ignore any weird quirks Proxmox has with the network
  # or cloud-init so it doesn't accidentally try to reboot the VM later.
  lifecycle {
    ignore_changes = [
      initialization,
      network_device[0].mac_address
    ]
  }
}