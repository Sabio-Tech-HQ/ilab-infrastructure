resource "proxmox_virtual_environment_container" "memos_notes" {
  description  = "Memos LXC"
  node_name    = "ilab-node-03"
  vm_id        = 350
  unprivileged = true

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  disk {
    datastore_id = "vmstore"
    size         = 8
  }

  cpu {
    cores = 1
  }

  memory {
    dedicated = 1024
  }

  features {
    nesting = true
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "memos-01"

    user_account {
      # Inject BOTH keys: The one from your variables (Mac), and the DevOps VM explicitly
      keys = [
        var.ssh_public_key,
        file("/home/jthairu/.ssh/id_ed25519.pub")
      ]
      password = var.ssh_password
    }

    ip_config {
      ipv4 {
        address = "${var.memos_ip}/24"
        gateway = "10.10.10.1"
      }
    }
  }

  # Build the jthairu user immediately after the container boots
  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = "root"
      # Use the devops VM's private key since you are running Terraform from the devops VM
      private_key = file("/home/jthairu/.ssh/id_ed25519") 
      host        = var.memos_ip
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
}