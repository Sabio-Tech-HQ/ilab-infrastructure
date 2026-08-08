resource "proxmox_virtual_environment_vm" "postgres_cluster" {
  for_each = {
    "01" = { vid = 131, ip = "10.10.10.201/24" }
    "02" = { vid = 119, ip = "10.10.10.202/24" }
    "03" = { vid = 132, ip = "10.10.10.203/24" }
  }

  name      = "postgres-${each.key}"
  node_name = "ilab-node-03"
  vm_id     = each.value.vid
  bios      = "seabios"

  clone {
    vm_id = 1009
    full  = true
  }

  scsi_hardware = "virtio-scsi-single"
  
  cpu {
    type  = "x86-64-v2-AES"
    cores = 4
  }
  
  memory {
    dedicated = 4096
  }
  
  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 50
    iothread     = true
    discard      = "on"
  }
  
  network_device {
    bridge   = "vmbr0"
    model    = "virtio"
    firewall = false
  }

  initialization {
    datastore_id = "vmstore"
    
    user_account {
      username = var.ssh_user
      password = var.ssh_password
      keys     = [
        var.ssh_public_key,
        file("/home/jthairu/.ssh/id_ed25519.pub")
      ]
    }

    ip_config {
      ipv4 {
        address = each.value.ip
        gateway = "10.10.10.1"
      }
    }
  }

  agent { 
    enabled = true 
    timeout = "1s"
  }

  # VM Lifecycle Shield goes here
  lifecycle {
    ignore_changes = [
      node_name, 
      network_device[0].mac_address,
      clone,
      bios,
      initialization
    ]
  }
}

resource "proxmox_virtual_environment_container" "postgres_04" {
  node_name    = "ilab-node-03"
  vm_id        = 206
  unprivileged = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  cpu { cores = 4 }
  memory {
    dedicated = 16384
    swap      = 512
  }
  
  disk {
    datastore_id = "vmstore"
    size         = 50
  }
  
  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }
  
  features {
    nesting = true
  }

  initialization {
    hostname = "postgres-04"
    
    user_account {
      password = var.ssh_password
      keys     = [
        var.ssh_public_key,
        file("/home/jthairu/.ssh/id_ed25519.pub")
      ]
    }
    ip_config {
      ipv4 {
        address = "10.10.10.206/24"
        gateway = "10.10.10.1"
      }
    }
  }

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "root"
      private_key = file("/home/jthairu/.ssh/id_ed25519") 
      host        = "10.10.10.206"
    }

    inline = [
      "useradd -m -s /bin/bash jthairu",
      "echo 'jthairu:${var.ssh_password}' | chpasswd",
      "echo 'jthairu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/jthairu",
      "mkdir -p /home/jthairu/.ssh",
      "cp /root/.ssh/authorized_keys /home/jthairu/.ssh/authorized_keys",
      "chown -R jthairu:jthairu /home/jthairu/.ssh",
      "chmod 700 /home/jthairu/.ssh",
      "chmod 600 /home/jthairu/.ssh/authorized_keys"
    ]
  }

  # Container Lifecycle Shield goes here (no unsupported attributes)
  lifecycle {
    ignore_changes = [
      network_interface[0].mac_address,
      initialization
    ]
  }
}