resource "proxmox_virtual_environment_vm" "wireguard_vpn" {
  name      = "wireguard"
  node_name = "ilab-node-02"
  vm_id     = 110

  # Match the existing BIOS hardware
  bios          = "ovmf"
  machine       = "q35"
  scsi_hardware = "virtio-scsi-single"

  cpu {
    cores = 2
    type  = "x86-64-v2-AES"
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
    model    = "virtio"
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 10
    file_format  = "raw"
    discard      = "on"   
    iothread     = true  
    replicate    = false 
  }

  # EFI disk settings that prevent "Force Replacement"
  efi_disk {
    datastore_id      = "vmstore"
    file_format       = "raw"
    pre_enrolled_keys = true  
    type              = "4m"    
  }

  initialization {
    datastore_id = "vmstore"
    ip_config {
      ipv4 {
        address = "10.10.10.20/24"
        gateway = "10.10.10.1"
      }
    }
  }
}