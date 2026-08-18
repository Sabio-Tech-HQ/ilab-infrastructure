# Master Homelab Service Inventory
Generated on: Fri Aug 14 08:18:38 AM UTC 2026
Host: devops

## Table of Contents
- [DATABASE-SERVERS-POSTGRES](#service-database-servers-postgres)
- [DATABASES-POSTGRES](#service-databases-postgres)
- [DEVOPS](#service-devops)
- [DNS](#service-dns)
- [HAPROXY](#service-haproxy)
- [HOMEASSISTANT](#service-homeassistant)
- [IT-TOOLS](#service-it-tools)
- [JELLYFIN](#service-jellyfin)
- [KAFKA](#service-kafka)
- [MCP](#service-mcp)
- [MEDIA](#service-media)
- [MEMOS](#service-memos)
- [MON-TOOLS](#service-mon-tools)
- [MSSQL-CLUSTER](#service-mssql-cluster)
- [OLLAMA](#service-ollama)
- [ORACLE-CLUSTER](#service-oracle-cluster)
- [PBS](#service-pbs)
- [PLEX](#service-plex)
- [TALOS](#service-talos)
- [TRAEFIK](#service-traefik)
- [UBUNTU-TEMPLATE](#service-ubuntu-template)
- [WEB-SERVER](#service-web-server)
- [WIREGUARD](#service-wireguard)


---
<a name="service-database-servers-postgres"></a>
# SERVICE: DATABASE-SERVERS-POSTGRES
Path: `services/database-servers-postgres`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_container.postgres_04](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_container) | resource |
| [proxmox_virtual_environment_vm.postgres_cluster](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:


---
<a name="service-databases-postgres"></a>
# SERVICE: DATABASES-POSTGRES
Path: `services/databases-postgres`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_postgresql"></a> [postgresql](#requirement\_postgresql) | 1.25.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_postgresql"></a> [postgresql](#provider\_postgresql) | 1.25.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [postgresql_database.airflow](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/database) | resource |
| [postgresql_database.media_dbs_log](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/database) | resource |
| [postgresql_database.media_dbs_main](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/database) | resource |
| [postgresql_database.pacs](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/database) | resource |
| [postgresql_database.vitals](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/database) | resource |
| [postgresql_grant.revoke_public_access](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/grant) | resource |
| [postgresql_role.app_roles](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/role) | resource |
| [postgresql_role.jthairu](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/role) | resource |
| [postgresql_role.media_users](https://registry.terraform.io/providers/cyrilgdn/postgresql/1.25.0/docs/resources/role) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_app_db_passwords"></a> [app\_db\_passwords](#input\_app\_db\_passwords) | Map of passwords for pacs, airflow, vitals | `map(string)` | n/a | yes |
| <a name="input_db_password"></a> [db\_password](#input\_db\_password) | n/a | `string` | n/a | yes |
| <a name="input_db_vip"></a> [db\_vip](#input\_db\_vip) | The Floating VIP pointing to HAProxy | `string` | n/a | yes |
| <a name="input_media_dbs_password"></a> [media\_dbs\_password](#input\_media\_dbs\_password) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
db_vip      = "10.10.10.200"


  pacs    = "Mucii1311254"
  airflow = "Mucii1311254"
  vitals  = "Mucii1311254"
}

```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/setup_etcd.yaml`
  ```yaml
  - name: Force Install Etcd via Binary (HTTP Mode)
    hosts: postgres-01, postgres-02, postgres-03
      - name: Download and Unpack
      - name: Unpack etcd
      - name: Move binaries
      - name: Ensure etcd user/group
          name: etcd
          name: etcd
      - name: STOP and PURGE etcd
      - name: Deploy etcd Systemd Unit
      - name: Reload and Start
          name: etcd
  ```
- `ansible/manage_proxies.yaml`
  ```yaml
  - name: Unified HAProxy and Keepalived Management
    hosts: haproxy
      - name: Allow non-local IP binding
        sysctl: { name: net.ipv4.ip_nonlocal_bind, value: '1', state: present, reload: yes }
      - name: Configure HAProxy
      - name: Restart HAProxy
        systemd: { name: haproxy, state: restarted, enabled: yes }
      - name: Configure Keepalived
      - name: Restart Keepalived
        systemd: { name: keepalived, state: restarted, enabled: yes }
  ```
- `ansible/setup_cluster.yaml`
  ```yaml
  - name: Bootstrap PostgreSQL 18 Cluster Nodes
    hosts: databases
      - name: Ensure apt keyrings directory exists
      - name: Download PostgreSQL repository key
      - name: Add PostgreSQL official apt repository
          filename: pgdg
      - name: Install dependencies
          name: 
      - name: Stop default Postgres (so Patroni can own 5432)
          name: postgresql
      - name: Remove default Postgres cluster to prevent conflicts
      - name: Create Patroni config directory
      - name: Deploy Patroni Config from Template
      - name: Ensure Patroni is started and enabled
          name: patroni
      - name: restart patroni
          name: patroni
  ```


---
<a name="service-devops"></a>
# SERVICE: DEVOPS
Path: `services/devops`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.devops](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:


---
<a name="service-dns"></a>
# SERVICE: DNS
Path: `services/dns`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.pihole](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```


---
<a name="service-haproxy"></a>
# SERVICE: HAPROXY
Path: `services/haproxy`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.haproxy_cluster](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/setup_haproxy.yaml`
  ```yaml
  - name: Fresh Deployment of HAProxy Cluster
    hosts: haproxy
      - name: 1. Install System Dependencies
          name: [haproxy, keepalived, socat, curl, psmisc]
      - name: 2. Allow Non-Local IP Binding
          name: net.ipv4.ip_nonlocal_bind
      - name: 3. Deploy HAProxy Config
      - name: 4. Deploy Keepalived Config
      - name: 5. Start HAProxy Service
          name: haproxy
      - name: 6. Start Keepalived Service
          name: keepalived
  ```


---
<a name="service-homeassistant"></a>
# SERVICE: HOMEASSISTANT
Path: `services/homeassistant`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.hass](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```


---
<a name="service-it-tools"></a>
# SERVICE: IT-TOOLS
Path: `services/it-tools`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_container.ittools](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_container) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_ittools_ip"></a> [ittools\_ip](#input\_ittools\_ip) | Static IP address for the Ollama LXC container | `string` | `"10.10.10.119"` | no |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | Proxmox API token ID (e.g., user@pam!tokenname) | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | Proxmox API token secret UUID | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | Proxmox API endpoint URL | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | Default root/user password | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]







```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-ittools.yaml`
  ```yaml
  - name: Deploy IT-Tools
    hosts: it-tools
      - name: Install prerequisite packages
          name:
      - name: Download Docker installation script
      - name: Run Docker installation script
      - name: Ensure Docker service is running and enabled
          name: docker
      - name: Ensure user is in the docker group
          name: "{{ ansible_user_id }}"
      - name: Reset connection to apply group membership
      - name: Create IT-Tools directory
      - name: Deploy docker-compose.yml for IT-Tools
                container_name: it-tools
      - name: Start IT-Tools container
  ```


---
<a name="service-jellyfin"></a>
# SERVICE: JELLYFIN
Path: `services/jellyfin`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.jellyfin](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-jellyfin.yaml`
  ```yaml
  - name: Deploy Jellyfin
    hosts: jellyfin  # Target host group defined in inventory.ini
    roles:
      - name: Ensure Python Docker SDK is installed
          name: python3-docker
      - name: Ensure Loki Docker driver is installed
          plugin_name: loki
      - name: Ensure Traefik network exists
          name: traefik_proxy
      - name: Create Media directory
      - name: Copy Docker Compose configuration
      - name: Pull and Start Docker Stack
  ```

### Sanitized Host and Group Configurations:
```yaml
```


---
<a name="service-kafka"></a>
# SERVICE: KAFKA
Path: `services/kafka`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.kafka_cluster](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-kafka.yaml`
  ```yaml
  - name: Deploy Kafka Service with Monitoring
    hosts: kafka
      - name: Ensure baseline tools are installed
          name: [docker.io, docker-compose-v2, curl, jq]
      - name: Create Kafka directory structure
      - name: Download JMX Exporter JAR
      - name: Deploy JMX Exporter Config
                name: kafka_server_brokertopicmetrics_$1
                name: kafka_server_$1_$2
                name: kafka_$1_$2_$3
      - name: Deploy Docker Compose Template
      - name: Restart Kafka
  ```


---
<a name="service-mcp"></a>
# SERVICE: MCP
Path: `services/mcp`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_container.mcp_gateway](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_container) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_mcp_ip"></a> [mcp\_ip](#input\_mcp\_ip) | Static IP address for the Ollama LXC container | `string` | `"10.10.10.109"` | no |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | Proxmox API token ID (e.g., user@pam!tokenname) | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | Proxmox API token secret UUID | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | Proxmox API endpoint URL | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | Default root/user password | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]







```


---
<a name="service-media"></a>
# SERVICE: MEDIA
Path: `services/media`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_postgresql"></a> [postgresql](#requirement\_postgresql) | 1.25.0 |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.media](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_media_vm_ip"></a> [media\_vm\_ip](#output\_media\_vm\_ip) | The primary IP address of the Media VM |

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-media.yaml`
  ```yaml
  - name: Deploy Media Stack
    hosts: media  # Target host group defined in inventory.ini
    roles:
      - name: Ensure Python Docker SDK is installed
          name: python3-docker
      - name: Ensure Loki Docker driver is installed
          plugin_name: loki
      - name: Ensure Traefik network exists
          name: traefik_proxy
      - name: Create Media directory
      - name: Copy Docker Compose configuration
      - name: Pull and Start Docker Stack
  ```

### Sanitized Host and Group Configurations:
```yaml
```


---
<a name="service-memos"></a>
# SERVICE: MEMOS
Path: `services/memos`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_container.memos_notes](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_container) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_cloud_init_image_id"></a> [cloud\_init\_image\_id](#input\_cloud\_init\_image\_id) | n/a | `string` | `null` | no |
| <a name="input_lxc_template_id"></a> [lxc\_template\_id](#input\_lxc\_template\_id) | n/a | `string` | `null` | no |
| <a name="input_memos_ip"></a> [memos\_ip](#input\_memos\_ip) | The static IP for the Memos LXC | `string` | `"10.10.10.35"` | no |
| <a name="input_memos_user"></a> [memos\_user](#input\_memos\_user) | The username for the Memos LXC | `string` | `"jthairu"` | no |
| <a name="input_node_template_map"></a> [node\_template\_map](#input\_node\_template\_map) | Map of Proxmox nodes to their specific template IDs | `map(number)` | <pre>{<br/>  "ilab-node-01": 1001,<br/>  "ilab-node-02": 1002,<br/>  "ilab-node-03": 1003<br/>}</pre> | no |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password for the instances | `string` | `""` | no |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the instances | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | n/a | `list(string)` | n/a | yes |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | `null` | no |
| <a name="input_target_node"></a> [target\_node](#input\_target\_node) | The Proxmox node where the VM/LXC will be installed (e.g., ilab-node-01) | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-memos.yaml`
  ```yaml
  - name: Provision Memos Environment
    hosts: memos_servers
      - name: Ensure jthairu user exists
          name: jthairu
      - name: Add SSH key for jthairu
      - name: Update apt cache and upgrade packages
      - name: Install prerequisite packages
          name:
      - name: Download Docker installation script
      - name: Run Docker installation script
      - name: Ensure Docker service is running and enabled
          name: docker
      - name: Add jthairu to docker group
          name: jthairu
      - name: Create Memos persistent data directory
      - name: Create docker-compose.yml for Memos
                container_name: memos
      - name: Start Memos container using Docker Compose
  ```


---
<a name="service-mon-tools"></a>
# SERVICE: MON-TOOLS
Path: `services/mon-tools`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.mon-tools](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-montools.yaml`


---
<a name="service-mssql-cluster"></a>
# SERVICE: MSSQL-CLUSTER
Path: `services/mssql-cluster`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.dc_server](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |
| [proxmox_virtual_environment_vm.sql_nodes](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_domain_admin_password"></a> [domain\_admin\_password](#input\_domain\_admin\_password) | n/a | `string` | n/a | yes |
| <a name="input_network_gateway"></a> [network\_gateway](#input\_network\_gateway) | n/a | `string` | `"10.10.10.1"` | no |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | `"https://10.10.10.103:8006/api2/json"` | no |
| <a name="input_template_name"></a> [template\_name](#input\_template\_name) | n/a | `string` | `"winserver2022-template-03"` | no |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/create-cluster.yml`
  ```yaml
  - name: Prepare and Create Windows Failover Cluster
    hosts: sql_nodes
      cluster_name: "MSSQL-CLUSTER"
      - name: Ensure Domain Admins and Service Account are Local Admins
          name: Administrators
      - name: Disable UAC Remote Restrictions
          name: LocalAccountTokenFilterPolicy
      - name: Create the cluster
      - name: Wait for Cluster to stabilize
      - name: Verify Cluster Status
      - name: Display Cluster Status
  ```
- `ansible/create-ag.yml`
  ```yaml
  - name: Configure SQL Always On Availability Group
    hosts: sql-node-01
      ag_name: "ILAB-AG01"
      listener_name: "ILAB-SQL-LST"
      - name: Ensure Mirroring Endpoints Exist (Run via Invoke-Sqlcmd)
      - name: Create the Availability Group
      - name: Create the AG Listener on .77
  ```
- `ansible/download-sql.yml`
  ```yaml
  - name: Force Download and Install SQL 2022 Developer
    hosts: sql_nodes
      - name: Clean and Create Install Directory
      - name: Download Bootstrapper
      - name: Use Bootstrapper to Download Full ISO
      - name: Verify ISO Existence
      - name: Mount ISO
      - name: Run Silent Install (Enterprise Features)
  ```
- `ansible/join-domain.yml`
  ```yaml
  - name: Join SQL Nodes to Domain
    hosts: sql_nodes
      domain_name: "ilab.local"
      - name: Join the ilab.local domain
          dns_domain_name: "{{ domain_name }}"
      - name: Reboot after joining domain
  ```
- `ansible/deploy-dc.yaml`
  ```yaml
  - name: Promote dc-01 to Domain Controller
    hosts: dc
      domain_name: "ilab.local"
      - name: Install AD-Domain-Services role
          name: AD-Domain-Services
      - name: Promote to Domain Controller (New Forest)
          dns_domain_name: "{{ domain_name }}"
      - name: Reboot after Promotion
  ```
- `ansible/secrets.yml`
  ```yaml
  ```
- `ansible/windows.yml`
  ```yaml
  domain_name: "ilab.local"
  ```
- `ansible/install-sql-instances.yml`
  ```yaml
  - name: SQL 2022 Installation (Virtual Account Method)
    hosts: sql_nodes
      - name: Mount SQL ISO
      - name: Run SQL Install (Using Virtual Account)
      - name: Set Service Account and Password (Post-Install)
          name: MSSQLSERVER
      - name: Enable Always On Feature
      - name: Unmount SQL ISO
  ```
- `ansible/configure-identity.yml`
  ```yaml
  - name: Configure Windows Identity and Static IPs
    hosts: all
      - name: Set Computer Hostname
        win_hostname:
          name: "{{ inventory_hostname }}"
      - name: Configure Static IP Address
      - name: Reboot to apply changes
  ```
- `ansible/create-service-account.yml`
  ```yaml
  - name: Create SQL Cluster Service Account
    hosts: dc
      csa_name: "sql_svc"
      - name: Create the service account in AD
          name: "{{ csa_name }}"
  - name: Grant Service Account Local Admin on SQL Nodes
    hosts: sql_nodes
      csa_name: "sql_svc" # Added here so this play knows the name
      - name: Add sql_svc to local Administrators group
          name: Administrators
  ```
- `ansible/install-cluster-features.yml`
  ```yaml
  - name: Install Failover Clustering Features
    hosts: sql_nodes
      - name: Install Failover-Clustering feature
          name: Failover-Clustering
      - name: Reboot if Cluster Feature requires it
  ```


---
<a name="service-ollama"></a>
# SERVICE: OLLAMA
Path: `services/ollama`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_container.ollama_ai](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_container) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_ollama_ip"></a> [ollama\_ip](#input\_ollama\_ip) | Static IP address for the Ollama LXC container | `string` | `"10.10.10.99"` | no |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | Proxmox API token ID (e.g., user@pam!tokenname) | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | Proxmox API token secret UUID | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | Proxmox API endpoint URL | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | Default root/user password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | Primary SSH public key | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"






```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-ai-stack.yaml`


---
<a name="service-oracle-cluster"></a>
# SERVICE: ORACLE-CLUSTER
Path: `services/oracle-cluster`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.oracle_nodes](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |
| [proxmox_virtual_environment_vm.storage_node](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-oracle.yaml`
  ```yaml
  - name: Configure Storage Gateway
    hosts: storage_gw
      - name: Ensure targetcli is ready
          name: targetcli-fb
  - name: Configure Oracle Nodes
    hosts: oracle_nodes
      - name: Locate Oracle Config Script
      - name: Ensure /etc/sysconfig/oracle-free-23ai.conf exists
      - name: Clean up failed DB attempts (Clean Slate)
      - name: Run Database Configuration (CDB/PDB Creation)
      - name: Finalize Environment Variables
  ```


---
<a name="service-pbs"></a>
# SERVICE: PBS
Path: `services/pbs`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.pbs](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-pbs.yaml`
  ```yaml
  - name: Deploy Proxmox Backup Server
    hosts: pbs
    roles:
  ```


---
<a name="service-plex"></a>
# SERVICE: PLEX
Path: `services/plex`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.plex](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-plex.yaml`
  ```yaml
  - name: Deploy Plex
    hosts: plex
    roles:
      - name: Ensure Python Docker SDK is installed
          name: python3-docker
      - name: Ensure Loki Docker driver is installed
          plugin_name: loki
      - name: Ensure Traefik network exists
          name: traefik_proxy
      - name: Create Plex and Beats directories
      - name: Copy Docker Compose and Beats configurations
      - name: Pull and Start Docker Stack
  ```

### Sanitized Host and Group Configurations:
```yaml
```


---
<a name="service-talos"></a>
# SERVICE: TALOS
Path: `services/talos`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |
| <a name="requirement_talos"></a> [talos](#requirement\_talos) | 0.7.0 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |
| <a name="provider_talos"></a> [talos](#provider\_talos) | 0.7.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.talos_nodes](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |
| [talos_cluster_kubeconfig.kubeconfig](https://registry.terraform.io/providers/siderolabs/talos/0.7.0/docs/resources/cluster_kubeconfig) | resource |
| [talos_machine_bootstrap.bootstrap](https://registry.terraform.io/providers/siderolabs/talos/0.7.0/docs/resources/machine_bootstrap) | resource |
| [talos_machine_configuration_apply.controlplane](https://registry.terraform.io/providers/siderolabs/talos/0.7.0/docs/resources/machine_configuration_apply) | resource |
| [talos_machine_secrets.cluster](https://registry.terraform.io/providers/siderolabs/talos/0.7.0/docs/resources/machine_secrets) | resource |
| [talos_machine_configuration.controlplane](https://registry.terraform.io/providers/siderolabs/talos/0.7.0/docs/data-sources/machine_configuration) | data source |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_mysql_root_password"></a> [mysql\_root\_password](#input\_mysql\_root\_password) | Password for mysql root | `string` | n/a | yes |
| <a name="input_pacs_password"></a> [pacs\_password](#input\_pacs\_password) | Password for the PACS MySQL user | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_talos_kubeconfig"></a> [talos\_kubeconfig](#output\_talos\_kubeconfig) | n/a |

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"






```


---
<a name="service-traefik"></a>
# SERVICE: TRAEFIK
Path: `services/traefik`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.traefik_vms](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-traefik.yaml`


---
<a name="service-ubuntu-template"></a>
# SERVICE: UBUNTU-TEMPLATE
Path: `services/ubuntu-template`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.ubuntu_template](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```


---
<a name="service-web-server"></a>
# SERVICE: WEB-SERVER
Path: `services/web-server`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.web-server](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_gateway"></a> [gateway](#input\_gateway) | n/a | `string` | n/a | yes |
| <a name="input_ip_address"></a> [ip\_address](#input\_ip\_address) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_password"></a> [ssh\_password](#input\_ssh\_password) | SSH password | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |
| <a name="input_ssh_public_keys"></a> [ssh\_public\_keys](#input\_ssh\_public\_keys) | The public SSH key to be injected into the VMs | `list(string)` | `[]` | no |
| <a name="input_ssh_user"></a> [ssh\_user](#input\_ssh\_user) | n/a | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-website.yaml`
  ```yaml
  - name: Deploy PACS and Mwakilishi Stacks
    hosts: web_servers
    roles:
  ```


---
<a name="service-wireguard"></a>
# SERVICE: WIREGUARD
Path: `services/wireguard`

## [Infrastructure] Terraform Structure
## Requirements

| Name | Version |
| ---- | ------- |
| <a name="requirement_proxmox"></a> [proxmox](#requirement\_proxmox) | 0.70.1 |

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_proxmox"></a> [proxmox](#provider\_proxmox) | 0.70.1 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [proxmox_virtual_environment_vm.wireguard_vpn](https://registry.terraform.io/providers/bpg/proxmox/0.70.1/docs/resources/virtual_environment_vm) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_proxmox_api_token_id"></a> [proxmox\_api\_token\_id](#input\_proxmox\_api\_token\_id) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_token_secret"></a> [proxmox\_api\_token\_secret](#input\_proxmox\_api\_token\_secret) | n/a | `string` | n/a | yes |
| <a name="input_proxmox_api_url"></a> [proxmox\_api\_url](#input\_proxmox\_api\_url) | n/a | `string` | n/a | yes |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | The public SSH key to be injected into the VMs | `string` | n/a | yes |

## Outputs

No outputs.

### Environment Runtime Variables (.tfvars):
```hcl
proxmox_api_url          = "https://10.10.10.102:8006/api2/json"


]
ssh_user = "jthairu"

ip_address = "10.10.10.90/24"
gateway = "10.10.10.1"





```

## [Provisioning] Ansible Automation
### Playbooks and Structural Layout:
- `ansible/deploy-wireguard.yaml`
  ```yaml
  - name: Deploy and Manage WireGuard
    hosts: vpn
      - name: Read Private Key
      - name: Initialize wg0.conf from template
      - name: Restart WireGuard
          name: "wg-quick@{{ vpn_interface }}"
  ```
- `ansible/add-peer.yaml`
  ```yaml
  - name: Add WireGuard Peer and Show QR Code
    hosts: vpn
      peer_name: "phone-jthairu"
      - name: Generate Peer Keys
      - name: Read Keys for Config Generation
      - name: Add Peer to Server Config
      - name: Generate Client Config File
      - name: Generate QR Code for Terminal
      - name: Display QR Code
      - name: Sync WireGuard
  ```
