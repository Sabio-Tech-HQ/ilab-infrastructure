resource "proxmox_virtual_environment_container" "immich" {
  description  = "Immich photo server — external library bound to jtnas photo share"
  node_name    = "ilab-node-01"
  vm_id        = 353
  unprivileged = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  disk {
    datastore_id = "vmstore"
    size         = 32
  }

  cpu {
    cores = 4
  }

  memory {
    dedicated = 6144
  }

  features {
    nesting = true
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }


  initialization {
    hostname = "immich-01"

    user_account {
      keys = [
        var.ssh_public_key,
        file("/home/jthairu/.ssh/id_ed25519.pub")
      ]
      password = var.ssh_password
    }

    ip_config {
      ipv4 {
        address = "${var.immich_ip}/24"
        gateway = "10.10.10.1"
      }
    }
  }

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "root"
      private_key = file("/home/jthairu/.ssh/id_ed25519")
      host        = var.immich_ip
    }

    inline = [
      "useradd -m -s /bin/bash jthairu",
      "echo 'jthairu:ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/jthairu",
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
