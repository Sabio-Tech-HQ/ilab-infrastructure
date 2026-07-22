# iLab Infrastructure 🚀

Central repository for managing the High Availability lab environment using **Ansible** and **Terraform**.

## 🌐 Network Map (The Source of Truth)

| Service | Component | IP Address | Hostname | Role |
| :--- | :--- | :--- | :--- | :--- |
| **Postgres HA** | **Virtual IP (VIP)** | **10.10.10.200** | `db-vip` | Entry Point |
| | HAProxy 01 | 10.10.10.204 | `haproxy-01` | Load Balancer |
| | HAProxy 02 | 10.10.10.205 | `haproxy-02` | Load Balancer (Backup) |
| | Database 01 | 10.10.10.201 | `postgres-01` | Patroni Node |
| | Database 02 | 10.10.10.202 | `postgres-02` | Patroni Node |
| | Database 03 | 10.10.10.203 | `postgres-03` | Patroni Node |
| **DevOps** | Management VM | 10.10.10.216 | `devops` | Ansible/TF Controller |

---

## 🛠 Project Structure
- `databases/postgres-ha/ansible`: Playbooks for Keepalived, Patroni, and Docker.
- `databases/postgres-ha/terraform`: Postgres DBs, Roles, and Permissions logic.

---

## 🚀 Quick Commands

### 🏗️ Terraform (Database Schema & Users)
*Run from `databases/postgres-ha/terraform/`*
```bash
# Preview changes without applying
terraform plan

# Apply changes (creates DBs, Users, etc.)
terraform apply

# See current state of resources
terraform show
```
### 🤖 Ansible (Infrastructure Maintenance)
*Run these from the project root.*

```bash
# Check if all nodes are alive
ansible all -i databases/postgres-ha/ansible/hosts.ini -m ping

# Apply a new Patroni configuration change
ansible-playbook -i databases/postgres-ha/ansible/hosts.ini databases/postgres-ha/ansible/apply_config.yml -K

# Rolling restart of the cluster (safe maintenance)
ansible-playbook -i databases/postgres-ha/ansible/hosts.ini databases/postgres-ha/ansible/rolling_restart.yml -K
```

### 🐘 Postgres Cluster Management (Patroni)
*Run these from the project root.*
```bash
# View cluster status (Run from DevOps VM)
ansible postgres_nodes -i databases/postgres-ha/ansible/hosts.ini -m shell -a "sudo patronictl list" -K

# Manually failover to a different node
ansible postgres-01 -i databases/postgres-ha/ansible/hosts.ini -m shell -a "sudo patronictl failover" -K
```
