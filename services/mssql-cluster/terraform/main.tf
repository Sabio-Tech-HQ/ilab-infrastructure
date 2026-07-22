# 1. New Domain Controller
resource "proxmox_virtual_environment_vm" "dc_server" {
  name        = "dc-01"
  description = "Managed by Terraform"
  tags        = ["windows", "dc"]
  node_name   = "ilab-node-03" # Changed from 02 to 03 to match plan
  bios        = "ovmf" 
  machine     = "pc-q35-10.1"
  scsi_hardware = "virtio-scsi-single"
  started     = true # Set to true so TF doesn't try to shut it down

  cpu {
    cores = 2
    type  = "kvm64" 
  }

  efi_disk { 
    datastore_id      = "vmstore"
    file_format       = "raw" 
    pre_enrolled_keys = true
    type              = "4m" 
  }

  memory {
    dedicated = 4096
  }

  agent { enabled = true }

  network_device {
    bridge = "vmbr0"
    mac_address = "BC:24:11:00:00:10"
  }

  operating_system { type = "win11" }

  tpm_state {
    version      = "v2.0"
    datastore_id = "vmstore"
  }

  lifecycle {
    ignore_changes = [
      started,           # Stop TF from toggling power
      network_device,    # Protect your unique MACs
      node_name,         # Protect against future migrations
      disk,              # Protect manual disk changes
      vga,               # Stop TF from trying to unset VGA (as seen in your plan)
      machine,
      scsi_hardware
    ]
  }
}

# 2. SQL Cluster Nodes
resource "proxmox_virtual_environment_vm" "sql_nodes" {
  count     = 3
  # Adjusted logic to match your current "Real" naming (1=01, 2=03, 3=02 based on plan)
  name      = count.index == 0 ? "sql-node-01" : (count.index == 1 ? "sql-node-03" : "sql-node-02")
  node_name = "ilab-node-03"
  bios      = "ovmf" 
  machine   = "q35"
  scsi_hardware = "virtio-scsi-single"
  started   = true 
  
  cpu {
    cores = 4
    type  = "kvm64" 
    numa  = true
  }

  memory { dedicated = 8192 }

  # OS Disk (Must be defined so TF doesn't try to delete it)
  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 32
  }

  # Data Disk
  disk {
    datastore_id = "vmstore" 
    interface    = "scsi1"
    size         = 100
    file_format  = "raw"
    iothread     = true
    discard      = "on"
    ssd          = true
  }

  agent { enabled = true }

  tpm_state {
    version      = "v2.0"
    datastore_id = "vmstore" 
  }

  efi_disk {  
    datastore_id      = "vmstore"
    file_format       = "raw" 
    pre_enrolled_keys = true 
    type              = "4m" 
  }

  network_device {
    bridge      = "vmbr0"
    # Match the MACs we know are working
    mac_address = count.index == 0 ? "BC:24:11:DF:DD:48" : (count.index == 1 ? "BC:24:11:00:00:23" : "BC:24:11:C5:4C:50")
  }

  operating_system { type = "win11" }

  lifecycle {
    ignore_changes = [
      started,
      network_device,
      node_name,
      disk,
      vga,
      machine,
      scsi_hardware,
      cpu[0].numa
    ]
  }
}