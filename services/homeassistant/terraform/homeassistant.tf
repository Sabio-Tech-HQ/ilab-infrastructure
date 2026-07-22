resource "proxmox_virtual_environment_vm" "hass" {
  name      = "home-assistant"
  node_name = "ilab-node-02"
  vm_id     = 100
  bios      = "ovmf"
  machine   = "q35"

  scsi_hardware = "virtio-scsi-single"

  description     = "Managed by Terraform."
  keyboard_layout = "en-us"
  on_boot         = true

  cpu {
    cores = 4
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = 8192
  }

  agent {
    enabled = true
    type    = "virtio"
  }

  efi_disk {
    datastore_id = "vmstore"
    file_format  = "raw"
    type         = "4m"
  }

  disk {
    datastore_id = "vmstore"
    file_format  = "raw"
    interface    = "scsi0"
    size         = 32
    iothread     = true
    discard      = "on"
    aio          = "io_uring"
    replicate    = false
  }

  network_device {
    bridge      = "vmbr0"
    model       = "virtio"
    firewall    = true
    mac_address = "BC:24:11:2E:C8:74"
  }

  operating_system {
    type = "l26"
  }

  lifecycle {
    prevent_destroy = true
  }
}