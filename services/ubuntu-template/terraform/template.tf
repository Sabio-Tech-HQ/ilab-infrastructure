resource "proxmox_virtual_environment_vm" "ubuntu_template" {
  name      = "ubuntu-template"
  node_name = "ilab-node-03"
  vm_id     = 1009
  bios      = "ovmf"

  on_boot         = false
  keyboard_layout = "en-us"
  machine         = "q35"
  scsi_hardware   = "virtio-scsi-single" 

  cpu {
    cores = 2
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = 4096 
  }

  # 1. The blank target hard drive for the installation
  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 20
    iothread     = true
    discard      = "on"
    replicate    = false
  }

  # 2. Attach the Ubuntu ISO as a CD-ROM boot source
  cdrom {
    enabled   = true
    file_id   = "jtnas:iso/ubuntu-24.04.4-live-server-amd64.iso"
    interface = "ide2"
  }
  
  efi_disk { 
    datastore_id      = "vmstore"
    file_format       = "raw" 
    pre_enrolled_keys = true 
    type              = "4m" 
  }
  
  agent {
    enabled = true 
    type    = "virtio"
  }

  operating_system {
    type = "l26" 
  }

  initialization {
    datastore_id = "vmstore"

    user_account {
      username = var.ssh_user
      keys     = var.ssh_public_keys
    }

    ip_config {
      ipv4 {
        address = "dhcp" 
      }
    }
  }

  network_device {
    bridge       = "vmbr0"
    disconnected = false
    enabled      = true
    firewall     = true 
  }

  description = "Managed by Terraform - Base Ubuntu Template."
}