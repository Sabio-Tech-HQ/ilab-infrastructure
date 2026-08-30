resource "proxmox_virtual_environment_container" "p_ngx" {
  description  = "Paperless NGX LXC"
  node_name    = "ilab-node-03"
  vm_id        = 355
  unprivileged = true

  operating_system {
    template_file_id = "jtnas:vztmpl/lxc-ubuntu-24.04-standard_24.04-2_amd64.tar.zst"
    type             = "ubuntu"
  }

  disk {
    datastore_id = "vmstore"
    size         = 25
  }

  # ============================================================
  # NAS BIND MOUNTS (Keeps your manual host mounts persistent)
  # ============================================================
  mount_point {
    volume = "/mnt/pve/jtnas/paperless/media"
    path   = "/opt/paperless/media"
  }

  mount_point {
    volume = "/mnt/pve/jtnas/paperless/consume"
    path   = "/opt/paperless/consume"
  }
  # ============================================================

  cpu {
    cores = 4
  }

  memory {
    dedicated = 4096
  }

  features {
    nesting = true
    # fuse = true <-- Commented out for stable initial container provisioning
  }

  network_interface {
    name   = "eth0"
    bridge = "vmbr0"
  }

  initialization {
    hostname = "paperless-ngx"

    user_account {
      keys = concat(
        var.ssh_public_keys,
        [file("/home/jthairu/.ssh/id_ed25519.pub")]
      )
      password = var.ssh_password
    }

    ip_config {
      ipv4 {
        address = "${var.pngx_ip}/24"
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
      host        = var.pngx_ip
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
      mount_point, # Protects the static NAS storage mappings from drift resets
      unprivileged,
    ]
  }
}
