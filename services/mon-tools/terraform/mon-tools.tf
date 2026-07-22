resource "proxmox_virtual_environment_vm" "mon-tools" {
  name      = "mon-tools"
  node_name = "ilab-node-03"
  vm_id     = 106
  bios      = "ovmf"

  on_boot         = true
  keyboard_layout = "en-us"

  machine        = "q35"

  scsi_hardware  = "virtio-scsi-single" 

  cpu {
          cores     = 4 
          type      = "x86-64-v2-AES"
  }

  memory {
           dedicated   =   8192 
  }

  disk {
    datastore_id = "vmstore"
    file_format  = "raw"
    interface    = "scsi0"
    size         = 115
    iothread     = true
    discard      = "on"
    replicate    = false
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

   network_device {
           bridge       = "vmbr0"
           disconnected = false
           enabled      = true
           firewall     = true 
           mac_address  = "BC:24:11:0D:17:40" 
   }

   description = "Managed by Terraform."

   timeout_create = 1800
   timeout_clone  = 1800

}