resource "proxmox_virtual_environment_container" "ittools" {
  description  = " IT Tools LXC"
  node_name    = "ilab-node-01"
  vm_id        = 111
  unprivileged = true

  operating_system {
    template_file_id = "jtnas:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  disk {
    datastore_id = "vmstore"
    size         = 8
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 2048
  }

  features {
    nesting = true
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "ittools"

    user_account {
      # Use concat() to cleanly merge your list of keys with the local devops key
      keys = concat(
        var.ssh_public_keys,
        [file("/home/jthairu/.ssh/id_ed25519.pub")]
      )
      password = var.ssh_password
    }

    ip_config {
      ipv4 {
        address = "${var.ittools_ip}/24"
        gateway = "10.10.10.1"
      }
    }
  }

  # Build the jthairu user immediately after the container boots
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "root"
      # NO agent = true here. We point directly to the devops VM private key.
      private_key = file("/home/jthairu/.ssh/id_ed25519") 
      host        = var.ittools_ip
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

  lifecycle {
    ignore_changes = [
      initialization,
      operating_system,
      network_interface[0].mac_address,
      unprivileged,
    ]
  }
}