import re

print("flowchart TD")
current_service = None

with open("homelab_services_master.md", "r") as f:
    for line in f:
        # Detect Service header
        if line.startswith("# SERVICE:"):
            current_service = line.replace("# SERVICE:", "").strip()
            print(f'\n  subgraph {current_service} ["{current_service}"]')
            
        # Detect Proxmox VM resources inside tables
        elif "proxmox_virtual_environment" in line:
            # Extract resource name
            match = re.search(r"proxmox_virtual_environment_\w+\.(\w+)", line)
            if match:
                res_name = match.group(1)
                print(f'    {res_name}[{res_name}]')
                
        # Close subgraph when hitting a divider line
        elif line.startswith("---") and current_service:
            print("  end")
            current_service = None

if current_service:
    print("  end")
