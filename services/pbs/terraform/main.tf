resource "proxmox_virtual_environment_vm" "pbs" {
  name      = "pbs"
  node_name = "ilab-node-03"
  vm_id     = 900
  bios      = "seabios"

  on_boot         = true
  keyboard_layout = "en-us"

  machine       = "q35"
  scsi_hardware = "virtio-scsi-pci" 

  cpu {
    cores = 2
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = 4096
  }

  disk {
    datastore_id = "vmstore"
    file_format  = "raw"
    interface    = "scsi0"
    size         = 32
    iothread     = true
    discard      = "on"
  }

  cdrom {
    enabled   = true
    file_id   = "none"
    interface = "ide2"
  }

  network_device {
    bridge      = "vmbr0"
    model       = "virtio"
    mac_address = "BC:24:11:D3:C4:39"
  }


  agent {
    enabled = true
    type    = "virtio"
  }

  operating_system {
    type = "l26"
  }

  description = "Managed by Terraform."

  timeout_create = 1800
  timeout_clone  = 1800

  provisioner "local-exec" {
    # No need for -i since it is defined in ansible.cfg
    command = "ansible-playbook ../ansible/deploy-pbs.yaml"
    working_dir = "${path.module}/../ansible" # Ensures it runs from the correct context
  }
  
}