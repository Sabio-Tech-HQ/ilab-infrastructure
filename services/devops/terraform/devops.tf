resource "proxmox_virtual_environment_vm" "devops" {
  name      = "devops"
  node_name = "ilab-node-02"
  vm_id     = 136
  bios      = "seabios"

  scsi_hardware = "virtio-scsi-single"

  keyboard_layout = "en-us"
  on_boot         = true

  cpu {
    cores = 4
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = 8192
  }

  operating_system {
    type = "l26" 
  }

  agent {
    enabled = true
    type    = "virtio"
  }

  # Adding the disk block to match your storage setup
  disk {
    datastore_id = "vmstore"
    file_format  = "raw"
    interface    = "scsi0"
    size         = 100
    iothread     = true
    discard      = "on"
    aio          = "io_uring"
    replicate    = false
  }

  network_device {
    bridge      = "vmbr0"
    disconnected = false 
    enabled      = true 
    firewall     = true 
    mac_address  = "BC:24:11:CA:C3:2C" 
    model        = "virtio"
  }

  lifecycle {
    prevent_destroy = true
  }
}