# iLab Infrastructure Documentation

**Generated**: 2026-08-21  
**Source**: ilab-infrastructure repository  
**Platform**: Proxmox VE (Terraform + Ansible)  
**Network**: 10.10.10.0/24 (vmbr0), 10.10.20.0/24 (vmbr1 - Oracle private)

---

## Table of Contents
1. [Proxmox Cluster Nodes](#proxmox-cluster-nodes)
2. [Virtual Machines (VMs)](#virtual-machines-vms)
3. [LXC Containers](#lxc-containers)
4. [Kubernetes Cluster (Talos)](#kubernetes-cluster-talos)
5. [Services Inventory by Host](#services-inventory-by-host)
6. [Database Clusters](#database-clusters)
7. [Network Topology](#network-topology)

---

## Proxmox Cluster Nodes

| Node | Hostname | Role |
|------|----------|------|
| Node 1 | ilab-node-01 | Control plane, DevOps, WireGuard, Talos CP |
| Node 2 | ilab-node-02 | Talos CP, Pi-hole |
| Node 3 | ilab-node-03 | Worker nodes, Media, Databases, SQL, Oracle, HAProxy, Vaultwarden, Penpot, Ollama, Pi-hole |

---

## Virtual Machines (VMs)

### 1. DevOps Management VM
- **Terraform**: `services/devops/terraform/devops.tf`
- **VM ID**: 136
- **Node**: ilab-node-01
- **IP**: 10.10.10.216
- **Specs**: 4 vCPU, 8 GB RAM, 100 GB disk (vmstore)
- **OS**: Ubuntu (l26)
- **MAC**: BC:24:11:CA:C3:2C
- **Purpose**: Ansible/Terraform controller, Docker host, Git repos, CI/CD
- **Services**:
  - Docker Engine + Compose
  - Ansible
  - Terraform
  - Tailscale
  - PostgreSQL Client 17
  - MySQL Client
  - PHP 8.4, Node.js, npm, Composer
  - Git repositories: ilab-infrastructure, mwakilishi/app, mdko-portal, nidate

---

### 2. HAProxy Cluster (2 VMs)
- **Terraform**: `services/haproxy/terraform/main.tf`
- **Node**: ilab-node-03
- **VM IDs**: Cloned from template 1009
- **IPs**: 10.10.10.204 (haproxy-01), 10.10.10.205 (haproxy-02)
- **VIP**: 10.10.10.200 (Keepalived)
- **Purpose**: Load balancer for PostgreSQL HA cluster
- **Services**:
  - HAProxy (TCP load balancing for PostgreSQL 5432)
  - Keepalived (VRRP for VIP failover)
  - Docker (via Ansible traefik role)

---

### 3. Vaultwarden Cluster (3 VMs)
- **Terraform**: `services/vaultwarden/terraform/vaultwarden.tf`
- **Node**: ilab-node-03
- **VM IDs**: Cloned from template 1009
- **IPs**: 10.10.10.207, 10.10.10.208, 10.10.10.209
- **Purpose**: Bitwarden-compatible password manager
- **Services** (per VM, Docker Compose):
  - vaultwarden/server:latest (port 80)
  - PostgreSQL backend via HAProxy VIP (10.10.10.200:5432)
  - Data volume: /opt/vaultwarden/data

---

### 4. WireGuard VPN
- **Terraform**: `services/wireguard/terraform/wireguard.tf`
- **VM ID**: 110
- **Node**: ilab-node-01
- **IP**: 10.10.10.20
- **Specs**: 2 vCPU, 2 GB RAM, 10 GB disk
- **BIOS**: OVMF, q35, EFI
- **Services**:
  - WireGuard (wg0 interface)
  - Ansible-managed peer configuration

---

### 5. Media Server VM
- **Terraform**: `services/media/terraform/media-vm.tf`
- **VM ID**: 101
- **Node**: ilab-node-03
- **IP**: 10.10.10.30
- **Specs**: 4 vCPU, 8 GB RAM, 45 GB disk
- **MAC**: BC:24:11:7B:C2:08
- **BIOS**: OVMF, q35, EFI
- **Services** (Docker Compose at /opt/media-stack):
  - *arr stack: radarr, sonarr, prowlarr, bazarr, lidarr, readarr
  - Download clients: qBittorrent, SABnzbd
  - Media servers: Jellyfin (10.10.10.65), Plex (10.10.10.60)
  - Management: Portainer, Overseerr, Tautulli, Homepage
  - Indexers: Jackett
  - NAS mounts: /volume1/downloads, /volume1/music, /volume1/video

---

### 6. Pi-hole DNS (3 VMs)
- **Terraform**: `services/pihole/terraform/main.tf`
- **Nodes**: ilab-node-02 (x2), ilab-node-03 (x1)
- **VM IDs**: 103, 115, 116
- **IPs**: 10.10.10.10, 10.10.10.11, 10.10.10.13
- **Specs**: 2 vCPU, 1 GB RAM, 25 GB disk each
- **BIOS**: OVMF, q35, EFI
- **Services**:
  - Pi-hole DNS/DHCP (port 53, 80 web UI)
  - Unbound recursive resolver
  - Keepalived VIP (10.10.10.50) for HA

---

### 7. MSSQL Cluster (4 VMs - Windows)
- **Terraform**: `services/mssql-cluster/terraform/main.tf`
- **Node**: ilab-node-03
- **VMs**:
  - **DC Server**: dc-01 (VM ID from template), 2 vCPU, 4 GB RAM, 32 GB OS disk, TPM v2, MAC BC:24:11:00:00:10
  - **SQL Nodes** (3x): sql-node-01/02/03, 4 vCPU (NUMA), 8 GB RAM, 32 GB OS + 100 GB data disks, TPM v2
    - MACs: BC:24:11:DF:DD:48, BC:24:11:00:00:23, BC:24:11:C5:4C:50
- **Services** (Ansible-managed):
  - Active Directory Domain Controller
  - SQL Server 2022 Always On Availability Groups
  - Windows Failover Cluster
  - Kerberos authentication

---

### 8. Oracle RAC Cluster (4 VMs)
- **Terraform**: `services/oracle-cluster/terraform/main.tf`
- **Node**: ilab-node-03
- **Networks**: vmbr0 (10.10.10.0/24), vmbr1 (10.10.20.0/24 - private interconnect)
- **VMs**:
  - **Storage Gateway**: oracle-storage-gw (VM ID 144), 32 GB OS + 80 GB shared disk, IPs: 10.10.10.144 / 10.10.20.144
  - **DB Nodes** (3x): oracle-node-01/02/03 (VM IDs 141, 142, 143), 2 vCPU, 4 GB RAM, 40 GB OS disk each
    - IPs: 10.10.10.141-143 / 10.10.20.141-143
- **Clone source**: Template VM 1003
- **Services**:
  - Oracle Database 19c/21c RAC
  - ASM (Automatic Storage Management) on shared disk
  - Private interconnect on vmbr1

---

### 9. PBS (Proxmox Backup Server)
- **Inventory**: 10.10.10.241 (ansible_user=root)
- **Purpose**: Backup target for Proxmox VMs/CTs
- **NAS mount**: /volume1/pbs → /mnt/datastore

---

### 10. Home Assistant
- **Inventory**: 10.10.10.80
- **Purpose**: Home automation hub

---

### 11. Jellyfin (separate from media VM)
- **Inventory**: 10.10.10.65
- **Purpose**: Media streaming server

---

### 12. Plex (separate from media VM)
- **Inventory**: 10.10.10.60
- **Purpose**: Media streaming server

---

### 13. Kafka Cluster (3 VMs)
- **Inventory**: 10.10.10.235, 10.10.10.236, 10.10.10.237
- **Node IDs**: 1, 2, 3
- **Services**:
  - Apache Kafka brokers
  - Kafka Connect (Debezium connectors for Postgres, Cassandra)
  - Plugins: PostgreSQL JDBC, Protobuf, Debezium API/Core/Postgres, Cassandra sink

---

### 14. MariaDB Cluster (3 VMs)
- **Inventory**:
  - Master: mariadb-01 (10.10.10.41)
  - Slaves: mariadb-02 (10.10.10.42), mariadb-03 (10.10.10.43)
- **MaxScale Proxies** (2 VMs):
  - maxscale-01 (10.10.10.46)
  - maxscale-02 (10.10.10.47)
- **VIP**: 10.10.10.50 (VRRP)
- **Services**:
  - MariaDB Galera Cluster
  - MaxScale read/write splitting
  - Keepalived for VIP

---

### 15. Traefik Ingress (3 VMs)
- **Inventory**: traefik-01 (10.10.10.16), traefik-02 (10.10.10.17), traefik-03 (10.10.10.18)
- **Services** (Docker Compose):
  - Traefik v3.6.6 (ports 80, 443, 8080)
  - ACME/Let's Encrypt via AWS Route53
  - Loki logging driver (10.10.10.90:3100)
  - Dynamic configuration via file provider
  - Docker socket integration for auto-discovery

---

### 16. Monitoring Stack (mon-tools)
- **Inventory**: 10.10.10.90
- **Services** (Docker Compose):
  - Grafana (admin password from vault)
  - Loki (log aggregation, port 3100)
  - Prometheus (metrics)
  - Elasticsearch 9.2.2
  - Kibana
  - SMTP alerting

---

### 17. Ollama AI
- **Terraform**: `services/ollama/terraform/main.tf` (LXC - see below)
- **Inventory**: 10.10.10.99
- **Note**: Actually deployed as LXC container (see LXC section)

---

### 18. Penpot
- **Terraform**: `services/penpot/terraform/penpot.tf` (LXC - see below)
- **Inventory**: 10.10.10.98
- **Note**: Actually deployed as LXC container (see LXC section)

---

### 19. MCP Gateway
- **Inventory**: mcp-gateway (10.10.10.109)
- **Purpose**: Model Context Protocol gateway

---

### 20. Web Servers / PACS
- **Inventory**: pacs-server (10.10.10.99), ittools (10.10.10.119)
- **Purpose**: 
  - PACS medical imaging server (Docker at /home/jthairu/docker)
  - mwakilishi.com web application
  - IT-Tools utility suite

---

### 21. Memos
- **Inventory**: 10.10.10.35
- **Purpose**: Note-taking application
- **Data**: /var/opt/memos

---

### 22. Oracle Storage Gateway
- **Inventory**: oracle-storage-gw (10.10.10.144)
- **Part of**: Oracle RAC cluster (see above)

---

### 23. Talos Kubernetes Nodes (3 VMs)
- **Terraform**: `services/talos/terraform/main.tf`
- **VMs**:
  - talos-01 (VM ID 120, Node: ilab-node-01, IP: 10.10.10.215)
  - talos-02 (VM ID 121, Node: ilab-node-02, IP: 10.10.10.174)
  - talos-03 (VM ID 122, Node: ilab-node-03, IP: 10.10.10.22)
- **Specs**: 4 vCPU (host passthrough), 4 GB RAM, 40 GB disk
- **Boot**: Talos ISO (local:iso/talos.iso)
- **Cluster**: ilab-cluster
- **KubePrism**: Enabled (port 7445)
- **Control Plane Endpoint**: https://10.10.10.215:6443

---

## LXC Containers

### 1. Ollama AI Container
- **Terraform**: `services/ollama/terraform/main.tf`
- **VM ID**: 351
- **Node**: ilab-node-03
- **IP**: 10.10.10.99 (var.ollama_ip)
- **Hostname**: ollama-01
- **Specs**: 8 vCPU, 16 GB RAM, 60 GB disk
- **Features**: nesting=true (for Docker-in-LXC)
- **Template**: Ubuntu 24.04 standard
- **Services** (Docker):
  - ollama/ollama:latest (LLM inference server)
  - Models: Qwen, others (~9GB+)
  - GPU passthrough configured for inference acceleration

---

### 2. Penpot Design Platform
- **Terraform**: `services/penpot/terraform/penpot.tf`
- **VM ID**: 352
- **Node**: ilab-node-03
- **IP**: 10.10.10.98 (var.penpot_ip)
- **Hostname**: penpot
- **Specs**: 2 vCPU, 4 GB RAM, 25 GB disk
- **Features**: nesting=true
- **Template**: Ubuntu 24.04 standard (jtnas:vztmpl/...)
- **Services** (Docker Compose at /opt/penpot):
  - penpotapp/frontend:latest (port 9001→8080)
  - penpotapp/backend:latest (port 6060)
  - penpotapp/exporter:latest (port 6061)
  - valkey/valkey:8 (Redis-compatible, port 6379)
  - **External DB**: PostgreSQL via HAProxy VIP (10.10.10.200:5432)
  - Domain: penpot.mwakilishi.com (via Traefik)

---

## Kubernetes Cluster (Talos)

### Cluster: ilab-cluster
- **Control Plane**: 3 nodes (all controlplane + worker)
- **CNI**: Not explicitly configured (likely Cilium/Calico via extraManifests)
- **DNS**: CoreDNS, hostDNS forwarding enabled
- **KubePrism**: Local load balancing on port 7445
- **etcd**: Embedded in control plane nodes
- **Service CIDR**: 10.96.0.0/12
- **Pod CIDR**: 10.244.0.0/16

### Nodes
| Name | VM ID | Proxmox Node | IP | Role |
|------|-------|--------------|-----|------|
| talos-01 | 120 | ilab-node-01 | 10.10.10.215 | Control Plane |
| talos-02 | 121 | ilab-node-02 | 10.10.10.174 | Control Plane |
| talos-03 | 122 | ilab-node-03 | 10.10.10.22 | Control Plane |

### Kubernetes Services (Deployed via Manifests)

#### PostgreSQL Operator (CNPG)
- **Manifest**: `services/k8s/databases/postgres/manifests/cluster.yaml`
- **Cluster**: postgres-cluster (3 instances)
- **Storage**: local-path StorageClass, 20Gi per instance
- **Bootstrap**: initdb → database: app_db, owner: app_user
- **Secrets**: postgres-app-secret, postgres-superuser
- **Service**: postgres-vip (LoadBalancer, MetalLB IP: 10.10.10.240)

#### MetalLB Load Balancer
- **Manifest**: `services/k8s/networking/metallb/manifests/pool.yaml`
- **Pool IP**: 10.10.10.240 (for postgres-vip)

#### Local Path Provisioner
- **Manifest**: `services/k8s/storage/local-path/manifests/storage-class.yaml`
- **StorageClass**: local-path

#### Postgres LoadBalancer Service
- **Manifest**: `services/k8s/postgres-lb.yaml`
- **IP**: 10.10.10.240 (forced via MetalLB)

---

## Services Inventory by Host

### 10.10.10.10 - pihole-01 (VM)
- Pi-hole DNS + Unbound
- Keepalived (VIP 10.10.10.50)

### 10.10.10.11 - pihole-02 (VM)
- Pi-hole DNS + Unbound
- Keepalived (VIP 10.10.10.50)

### 10.10.10.13 - pihole-03 (VM)
- Pi-hole DNS + Unbound
- Keepalived (VIP 10.10.10.50)

### 10.10.10.16 - traefik-01 (VM)
- Traefik v3.6.6 (ingress)
- Docker socket integration
- Loki logging

### 10.10.10.17 - traefik-02 (VM)
- Traefik v3.6.6 (ingress)
- Docker socket integration
- Loki logging

### 10.10.10.18 - traefik-03 (VM)
- Traefik v3.6.6 (ingress)
- Docker socket integration
- Loki logging

### 10.10.10.20 - wireguard-01 (VM)
- WireGuard VPN server
- wg0 interface

### 10.10.10.22 - talos-03 (VM)
- Talos Linux control plane + worker
- Kubernetes API (6443)
- KubePrism (7445)
- etcd member

### 10.10.10.30 - media (VM)
- Docker Compose media stack (/opt/media-stack)
- *arr apps, downloaders, media servers
- NAS mounts (CIFS)

### 10.10.10.35 - memos_notes (VM)
- Memos note-taking app
- Data: /var/opt/memos

### 10.10.10.41 - mariadb-01 (VM)
- MariaDB Galera Master
- MaxScale target

### 10.10.10.42 - mariadb-02 (VM)
- MariaDB Galera Slave
- MaxScale target

### 10.10.10.43 - mariadb-03 (VM)
- MariaDB Galera Slave
- MaxScale target

### 10.10.10.46 - maxscale-01 (VM)
- MaxScale proxy (read/write split)
- Keepalived (VIP 10.10.10.50)

### 10.10.10.47 - maxscale-02 (VM)
- MaxScale proxy (read/write split)
- Keepalived (VIP 10.10.10.50)

### 10.10.10.60 - plex (VM)
- Plex Media Server

### 10.10.10.65 - jellyfin (VM)
- Jellyfin Media Server

### 10.10.10.66 - Talos Control Plane Endpoint (VIP)
- Kubernetes API: https://10.10.10.66:6443
- Note: This appears in Talos config as endpoint, may be MetalLB VIP

### 10.10.10.80 - hass (VM)
- Home Assistant

### 10.10.10.90 - mon (VM)
- Grafana, Loki, Prometheus, Elasticsearch, Kibana
- Loki endpoint: http://10.10.10.90:3100/loki/api/v1/push

### 10.10.10.98 - penpot (LXC, VM ID 352)
- Penpot frontend (9001), backend (6060), exporter (6061)
- Valkey (6379)
- External PostgreSQL via HAProxy VIP

### 10.10.10.99 - ollama_ai (LXC, VM ID 351) / pacs-server
- Ollama LLM inference (Docker)
- PACS medical imaging (Docker at /home/jthairu/docker)
- Note: Same IP for both LXC and VM in inventory - verify

### 10.10.10.109 - mcp-gateway (VM)
- MCP Gateway

### 10.10.10.119 - ittools (VM)
- IT-Tools utility suite

### 10.10.10.141 - oracle-node-01 (VM)
- Oracle RAC Node 1
- Private IP: 10.10.20.141

### 10.10.10.142 - oracle-node-02 (VM)
- Oracle RAC Node 2
- Private IP: 10.10.20.142

### 10.10.10.143 - oracle-node-03 (VM)
- Oracle RAC Node 3
- Private IP: 10.10.20.143

### 10.10.10.144 - oracle-storage-gw (VM)
- Oracle Storage Gateway / NFS for ASM
- Private IP: 10.10.20.144
- Shared disk: 80 GB (scsi1)

### 10.10.10.174 - talos-02 (VM)
- Talos Linux control plane + worker
- Kubernetes API (6443)
- KubePrism (7445)
- etcd member

### 10.10.10.200 - db-vip / haproxy_vip (VIP)
- HAProxy Keepalived VIP
- PostgreSQL entry point (port 5432)
- Used by: Vaultwarden, Penpot, PACS, mwakilishi, CNPG

### 10.10.10.201 - postgres-01 (VM)
- Patroni PostgreSQL Node 1
- Part of HA cluster behind HAProxy

### 10.10.10.202 - postgres-02 (VM)
- Patroni PostgreSQL Node 2

### 10.10.10.203 - postgres-03 (VM)
- Patroni PostgreSQL Node 3

### 10.10.10.204 - haproxy-01 (VM)
- HAProxy primary
- Keepalived MASTER for VIP 10.10.10.200

### 10.10.10.205 - haproxy-02 (VM)
- HAProxy backup
- Keepalived BACKUP for VIP 10.10.10.200

### 10.10.10.207 - vaultwarden-01 (VM)
- Vaultwarden instance 1
- PostgreSQL via VIP 10.10.10.200

### 10.10.10.208 - vaultwarden-02 (VM) / airflow
- Vaultwarden instance 2
- Airflow scheduler/worker

### 10.10.10.209 - vaultwarden-03 (VM)
- Vaultwarden instance 3

### 10.10.10.215 - talos-01 (VM)
- Talos Linux control plane + worker
- Kubernetes API endpoint: https://10.10.10.215:6443
- KubePrism (7445)
- etcd member

### 10.10.10.216 - devops (VM)
- Ansible/Terraform controller
- Docker host
- Git repos
- PostgreSQL/MySQL clients

### 10.10.10.235 - kafka node 1 (VM)
- Kafka broker (node_id=1)
- Kafka Connect with Debezium

### 10.10.10.236 - kafka node 2 (VM)
- Kafka broker (node_id=2)

### 10.10.10.237 - kafka node 3 (VM)
- Kafka broker (node_id=3)

### 10.10.10.240 - MetalLB IP (K8s)
- Forced IP for postgres-loadbalancer service
- PostgreSQL in Kubernetes (CNPG)

### 10.10.10.241 - pbs (VM)
- Proxmox Backup Server
- Root access via SSH
- NAS mount: /volume1/pbs → /mnt/datastore

---

## Database Clusters Summary

| Cluster | Type | Nodes | VIP/Endpoint | Purpose |
|---------|------|-------|--------------|---------|
| PostgreSQL HA | Patroni + HAProxy | 3 (201-203) | 10.10.10.200:5432 | Primary relational DB |
| PostgreSQL K8s | CNPG (CloudNativePG) | 3 | 10.10.10.240:5432 | Kubernetes-native PostgreSQL |
| MariaDB | Galera + MaxScale | 3 (41-43) + 2 proxies | 10.10.10.50:3306 | MySQL-compatible |
| MSSQL | Always On AG | 3 SQL + 1 DC | Listener (TBD) | Windows SQL Server |
| Oracle | RAC | 3 DB + 1 Storage | SCAN (TBD) | Oracle Enterprise |
| Valkey/Redis | Standalone | Per service | localhost:6379 | Caching/sessions |
| Kafka | KRaft/Cluster | 3 brokers | 235-237:9092 | Event streaming |

---

## Network Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROXMOX CLUSTER (3 Nodes)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                       │
│  │ ilab-node-01 │  │ ilab-node-02 │  │ ilab-node-03 │                       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                       │
└─────────┼─────────────────┼─────────────────┼────────────────────────────────┘
          │                 │                 │
    ┌─────┴─────┐     ┌─────┴─────┐     ┌─────┴──────────────────────────────┐
    │ vmbr0     │     │ vmbr0     │     │ vmbr0 (10.10.10.0/24)              │
    │ (LAN)     │     │ (LAN)     │     │ vmbr1 (10.10.20.0/24) Oracle only  │
    └─────┬─────┘     └─────┬─────┘     └─────┬──────────────────────────────┘
          │                 │                 │
    ┌─────┴─────┐     ┌─────┴─────┐     ┌─────┴──────────────────────────────┐
    │ DevOps    │     │ Talos-02  │     │ Talos-03                           │
    │ WireGuard │     │ Pi-hole-02│     │ Media, DBs, SQL, Oracle, HAProxy,  │
    │ Talos-01  │     │ Pi-hole-03│     │ Vaultwarden, Penpot, Ollama, Pi-hole│
    └───────────┘     └───────────┘     └────────────────────────────────────┘

Key VIPs:
- 10.10.10.50  → Pi-hole / MariaDB MaxScale (Keepalived)
- 10.10.10.200 → PostgreSQL HAProxy (Keepalived)
- 10.10.10.240 → K8s MetalLB (PostgreSQL CNPG)
- 10.10.10.66  → Talos Control Plane Endpoint (KubePrism/MetalLB)
```

---

## Storage

| Datastore | Type | Used By |
|-----------|------|---------|
| vmstore | Local/ZFS/NFS | All VM disks, ISOs, templates |
| jtnas (10.10.10.95) | Synology NAS | CIFS mounts: downloads, music, video, pbs |
| local | Proxmox local | ISO images (talos.iso), LXC templates |

---

## Ansible Group Variables (Key References)

From `ansible/group_vars/all/vars.yml`:
- **NAS**: 10.10.10.95 (jtnas)
- **PostgreSQL**: 10.10.10.200 (haproxy_vip)
- **MariaDB VIP**: 10.10.10.50 (vrrp_vip)
- **Loki**: http://10.10.10.90:3100/loki/api/v1/push
- **Kafka Brokers**: 10.10.10.235, 236, 237
- **Traefik**: /opt/traefik, ACME via AWS Route53
- **Media paths**: /opt/plex, /opt/jellyfin, /opt/media-stack, /home/jthairu/docker

---

## Secrets Management

All sensitive values stored in Ansible Vault (`ansible/vaults/legacy-vault.yml`) and Bitwarden:
- Database passwords (PostgreSQL, MariaDB, MSSQL, Oracle, Vaultwarden, Penpot, PACS, mwakilishi)
- NAS credentials
- AWS credentials (Route53 for ACME)
- SMTP credentials
- Grafana admin password
- JWT/encryption keys (Airflow fernet, Kibana, Vaultwarden)
- SSH keys (Bitwarden item: devops-ansible)
- Plex claim token
- Tailscale auth key

---

## Deployment Commands

### Terraform (per service)
```bash
cd services/<service>/terraform
./run-terraform.sh
# or
terraform init && terraform plan && terraform apply
```

### Ansible (per service)
```bash
cd services/<service>/ansible
./run-ansible.sh
# or
ansible-playbook -i inventory.ini deploy-<service>.yaml
```

### Root Ansible
```bash
cd ansible
ansible-playbook -i inventory.ini <playbook>.yaml
```

---

## Notes & Observations

1. **IP Conflict**: 10.10.10.99 appears in inventory for both `ollama` (LXC) and `pacs-server` / `web_servers` - verify actual deployment
2. **Talos Endpoint**: Two different endpoints in configs: 10.10.10.215 (main.tf) and 10.10.10.66 (controlplane.yaml) - 10.10.10.66 likely a MetalLB VIP
3. **Pi-hole IPs**: Terraform uses 10/11/13 but inventory shows 11/12/13 - verify actual
4. **MSSQL Naming**: Terraform creates sql-node-01, 03, 02 (non-sequential) to match existing MACs
5. **Template VMs**: Several resources clone from templates (1009, 1003, 1009) - ensure templates exist
6. **Kubernetes PostgreSQL**: Two PostgreSQL deployments - HAProxy/Patroni (VM-based) and CNPG (K8s-based) on different IPs (200 vs 240)

---

*Document generated from repository analysis. Verify IPs and services against running infrastructure.*