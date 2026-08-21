resource "proxmox_virtual_environment_container" "penpot" {
  description  = "Penpot LXC"
  node_name    = "ilab-node-03"
  vm_id        = 352
  unprivileged = true

  operating_system {
    template_file_id = "jtnas:vztmpl/lxc-ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  disk {
    datastore_id = "vmstore"
    size         = 25
  }

  cpu {
    cores = 2
  }

  memory {
    dedicated = 4096
  }

  features {
    nesting = true
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "penpot"

   user_account {
   keys = concat(
    var.ssh_public_keys,
    [file("/home/jthairu/.ssh/id_ed25519.pub")]
   )
   password = var.ssh_password
   }

  ip_config {
      ipv4 {
        address = "${var.penpot_ip}/24"
        gateway = "10.10.10.1"
      }
    }
  }

  # Build the jthairu user immediately after the container boots
  provisioner "remote-exec" {
  connection {
    type        = "ssh"
    user        = "root"
    private_key = file("/home/jthairu/.ssh/id_ed25519")
    host        = var.penpot_ip
    agent       = false
  }

  inline = [
    "id -u jthairu >/dev/null 2>&1 || useradd -m -s /bin/bash jthairu",
    "mkdir -p /home/jthairu/.ssh",
    "cp /root/.ssh/authorized_keys /home/jthairu/.ssh/authorized_keys",
    "chown -R jthairu:jthairu /home/jthairu/.ssh",
    "chmod 700 /home/jthairu/.ssh",
    "chmod 600 /home/jthairu/.ssh/authorized_keys",

    "printf '%s\\n' 'jthairu ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/jthairu",
    "chown root:root /etc/sudoers.d/jthairu",
    "chmod 0440 /etc/sudoers.d/jthairu",
    "visudo -cf /etc/sudoers.d/jthairu"
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