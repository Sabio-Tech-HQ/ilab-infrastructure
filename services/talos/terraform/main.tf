locals {
  talos_nodes = {
    "talos-01" = { id = 120, node = "ilab-node-01", ip = "10.10.10.215" }
    "talos-02" = { id = 121, node = "ilab-node-02", ip = "10.10.10.174" }
    "talos-03" = { id = 122, node = "ilab-node-03", ip = "10.10.10.22" }
  }
}

# ==========================================
# 1. PROXMOX VM CREATION
# ==========================================
resource "proxmox_virtual_environment_vm" "talos_nodes" {
  for_each = local.talos_nodes

  name      = each.key
  vm_id     = each.value.id
  node_name = each.value.node

  agent {
    enabled = false
  }

  operating_system {
    type = "l26" 
  }

  cpu {
    cores = 4
    type  = "host" 
  }

  memory {
    dedicated = 4096
  }

  cdrom {
    enabled   = true
    file_id   = "local:iso/talos.iso"
    interface = "ide2"
  }

  disk {
    datastore_id = "vmstore"
    interface    = "scsi0"
    size         = 40
    file_format  = "raw" 
  }

  network_device {
    bridge = "vmbr0"
    model  = "virtio"
  }

  boot_order = ["scsi0", "ide2"]
}

# ==========================================
# 2. TALOS SECRETS & CONFIGURATION
# ==========================================
resource "talos_machine_secrets" "cluster" {}

data "talos_machine_configuration" "controlplane" {
  for_each         = local.talos_nodes
  cluster_name     = "ilab-cluster"
  machine_type     = "controlplane"
  cluster_endpoint = "https://${local.talos_nodes["talos-01"].ip}:6443"
  machine_secrets  = talos_machine_secrets.cluster.machine_secrets
}

# ==========================================
# 3. PUSH CONFIG TO VMs
# ==========================================
resource "talos_machine_configuration_apply" "controlplane" {
  for_each                    = local.talos_nodes
  client_configuration        = talos_machine_secrets.cluster.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane[each.key].machine_configuration
  endpoint                    = each.value.ip
  node                        = each.value.ip
  
  depends_on = [proxmox_virtual_environment_vm.talos_nodes]
}

# ==========================================
# 4. BOOTSTRAP KUBERNETES CLUSTER
# ==========================================
resource "talos_machine_bootstrap" "bootstrap" {
  client_configuration = talos_machine_secrets.cluster.client_configuration
  endpoint             = local.talos_nodes["talos-01"].ip
  node                 = local.talos_nodes["talos-01"].ip
  
  depends_on = [talos_machine_configuration_apply.controlplane]
}

# ==========================================
# 5. EXTRACT KUBECONFIG
# ==========================================
resource "talos_cluster_kubeconfig" "kubeconfig" {
  client_configuration = talos_machine_secrets.cluster.client_configuration
  endpoint             = local.talos_nodes["talos-01"].ip
  node                 = local.talos_nodes["talos-01"].ip
  
  depends_on = [talos_machine_bootstrap.bootstrap]
}

output "talos_kubeconfig" {
  value     = talos_cluster_kubeconfig.kubeconfig.kubeconfig_raw
  sensitive = true
}