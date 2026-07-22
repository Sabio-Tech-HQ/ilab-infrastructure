resource "proxmox_virtual_environment_vm" "web-server" {
  name      = "web-server"
  node_name = "ilab-node-03"
  vm_id     = 122

  bios          = "ovmf"
  description   = "Managed by Terraform."
  machine       = "q35"
  scsi_hardware = "virtio-scsi-single"

  on_boot         = true
  keyboard_layout = "en-us"
  migrate         = false
  reboot          = false
  stop_on_destroy = false

  efi_disk {
    datastore_id      = "vmstore"
    pre_enrolled_keys = true
    type              = "4m"
  }

  agent {
    enabled = true
    type    = "virtio"
  }

  cpu {
    cores   = 1
    sockets = 4
    type    = "x86-64-v2-AES"
    units   = 1024
  }

  memory {
    dedicated = 8192
    shared    = 0
  }

  operating_system {
    type = "l26"
  }

  network_device {
    bridge      = "vmbr0"
    model       = "virtio"
    mac_address = "BC:24:11:72:42:A6"
    firewall    = false 
  }

  initialization {
    datastore_id = "vmstore" 
  }

  # Adding these prevents the "timeout" additions in every plan output
  timeout_clone      = 1800
  timeout_create     = 1800
  timeout_migrate    = 1800
  timeout_move_disk  = 1800
  timeout_reboot     = 1800
  timeout_shutdown_vm = 1800
  timeout_start_vm   = 1800
  timeout_stop_vm    = 300
}