#!/bin/bash

OUTPUT_FILE="homelab_services_master.md"
echo "# Master Homelab Service Inventory" > "$OUTPUT_FILE"
echo "Generated on: $(date)" >> "$OUTPUT_FILE"
echo "Host: $(hostname)" >> "$OUTPUT_FILE"
echo -e "\n## Table of Contents" >> "$OUTPUT_FILE"

# 1. Table of Contents
find . -maxdepth 1 -type d -not -name '.' -not -name '.*' | sort | while read -r service_dir; do
    service_name=$(basename "$service_dir")
    if [ -d "$service_dir/terraform" ] || [ -d "$service_dir/ansible" ]; then
        echo "- [${service_name^^}](#service-${service_name})" >> "$OUTPUT_FILE"
    fi
done

# 2. Process Folders
find . -maxdepth 1 -type d -not -name '.' -not -name '.*' | sort | while read -r service_dir; do
    service_name=$(basename "$service_dir")
    
    if [ -d "$service_dir/terraform" ] || [ -d "$service_dir/ansible" ]; then
        echo -e "\n\n---" >> "$OUTPUT_FILE"
        echo -e "<a name=\"service-${service_name}\"></a>" >> "$OUTPUT_FILE"
        echo -e "# SERVICE: ${service_name^^}" >> "$OUTPUT_FILE"
        echo -e "Path: \`services/${service_name}\`" >> "$OUTPUT_FILE"
    else
        continue
    fi
    
    # --- Terraform Architecture & Layout ---
    if [ -d "$service_dir/terraform" ] && ls "$service_dir/terraform"/*.tf >/dev/null 2>&1; then
        echo -e "\n## [Infrastructure] Terraform Structure" >> "$OUTPUT_FILE"
        terraform-docs markdown table "$service_dir/terraform" >> "$OUTPUT_FILE"
        
        # Extract sanitized variables (IPs, Node designations)
        if ls "$service_dir/terraform"/*.tfvars >/dev/null 2>&1; then
            echo -e "\n### Environment Runtime Variables (.tfvars):" >> "$OUTPUT_FILE"
            echo "\`\`\`hcl" >> "$OUTPUT_FILE"
            # Filter out sensitive configurations and cryptographic SSH keys
            cat "$service_dir/terraform"/*.tfvars | grep -ivE "password|secret|token|key|pwd|vault|ssh-rsa|ssh-ed25519|ecdsa|openssh" >> "$OUTPUT_FILE"
            echo "\`\`\`" >> "$OUTPUT_FILE"
        fi
    fi
    
    # --- Ansible Blueprints & Target Groups ---
    if [ -d "$service_dir/ansible" ]; then
        echo -e "\n## [Provisioning] Ansible Automation" >> "$OUTPUT_FILE"
        
        if [ -f "$service_dir/ansible/README.md" ]; then
            echo -e "### Role/Playbook Documentation:\n" >> "$OUTPUT_FILE"
            cat "$service_dir/ansible/README.md" >> "$OUTPUT_FILE"
        else
            echo -e "### Playbooks and Structural Layout:" >> "$OUTPUT_FILE"
            find "$service_dir/ansible" -maxdepth 2 \( -name "*.yml" -o -name "*.yaml" -o -name "hosts" -o -name "inventory" \) | while read -r config_file; do
                echo "- \`ansible/$(basename "$config_file")\`" >> "$OUTPUT_FILE"
                
                if [[ "$(wc -l < "$config_file")" -lt 120 ]]; then
                    echo "  \`\`\`yaml" >> "$OUTPUT_FILE"
                    grep -E "name:|hosts:|roles:" "$config_file" | sed 's/^/  /' >> "$OUTPUT_FILE"
                    echo "  \`\`\`" >> "$OUTPUT_FILE"
                fi
            done
        fi
        
        # Parse runtime Ansible host and group vars safely
        if [ -d "$service_dir/ansible/host_vars" ] || [ -d "$service_dir/ansible/group_vars" ]; then
            echo -e "\n### Sanitized Host and Group Configurations:" >> "$OUTPUT_FILE"
            echo "\`\`\`yaml" >> "$OUTPUT_FILE"
            find "$service_dir/ansible/host_vars" "$service_dir/ansible/group_vars" -type f \( -name "*.yml" -o -name "*.yaml" \) 2>/dev/null | while read -r var_file; do
                echo "# File: ansible/$(basename "$(dirname "$var_file")")/$(basename "$var_file")" >> "$OUTPUT_FILE"
                # Exclude secret strings, encrypted lines, vault pointers, and cryptographic keys
                cat "$var_file" | grep -ivE "password|secret|token|key|pwd|vault|\!vault|ssh-rsa|ssh-ed25519|ecdsa|openssh" >> "$OUTPUT_FILE"
            done
            echo "\`\`\`" >> "$OUTPUT_FILE"
        fi
    fi
done

echo "🎉 Enhanced data compilation complete: $OUTPUT_FILE"
