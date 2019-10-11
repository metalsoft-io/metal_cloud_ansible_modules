# metal_cloud_ansible_modules
Ansible modules for controlling the metal cloud.

#install metal-cloud-sdk python dependency.
pip install metal-cloud-sdk

#create group_vars directory and create a general variables file
```
cat group_vars/all/metalcloud.yml 
---
metalcloud_api_key: "<api_key>"
metalcloud_api_endpoint: "https://api.bigstep.com/metal-cloud"
metalcloud_user: "user@bigstep.com"
```

## Examples:
### To create an infrastructure:
```
---
- hosts: localhost
  vars: 
    infrastructure_label: "my-ansible-infra-13"
  tasks:
    - name: create a blank infrastructure
      metalcloud_infrastructure: 
        infrastructure_label: "{{infrastructure_label}}"
        datacenter_name: 'uk-reading'
        user: "{{metalcloud_user}}"
        api_key: "{{metalcloud_api_key}}"
        api_endpoint: "{{metalcloud_api_endpoint}}"
      register: infrastructure

    - name: create first instance array with a single instance with a minimum of 8 cores and 32 GB of RAM
      metalcloud_instance_array:
        infrastructure_id: "{{infrastructure.infrastructure_id}}"
        instance_array_label: 'my-test'
        instance_array_instance_count: 1  
        instance_array_ram_gbytes: 32
        instance_array_processor_core_count: 8
        instance_array_processor_count: 1 
        instance_array_firewall_rules:
             - firewall_rule_description: 'allow ssh'
               firewall_rule_protocol: 'tcp'
               firewall_rule_port_range_start: 22
               firewall_rule_port_range_end: 22
               firewall_rule_ip_address_type: 'ipv4'
               firewall_rule_source_ip_address_range_start: '0.0.0.0'
               firewall_rule_source_ip_address_range_end: '0.0.0.0'
               firewall_rule_source_ip_address_range_start: '0.0.0.0'
               firewall_rule_source_ip_address_range_end: '0.0.0.0'

        user: "{{metalcloud_user}}"
        api_key: "{{metalcloud_api_key}}"
        api_endpoint: "{{metalcloud_api_endpoint}}"
      register: intance_array_1
        
    - name: create a drive array that is bootable with 60GB SSD
      metalcloud_drive_array:
         infrastructure_id: "{{infrastructure.infrastructure_id}}"
         instance_array_id: "{{intance_array_1.instance_array_id}}"
         drive_array_label: 'centos-76'
         volume_template_label: 'centos7-6'
         drive_size_mbytes_default: 60000
         user: "{{metalcloud_user}}"
         api_key: "{{metalcloud_api_key}}"
         api_endpoint: "{{metalcloud_api_endpoint}}"

    - name: deploy changes if needed.
      metalcloud_infrastructure_deploy:
         infrastructure_id: "{{infrastructure.infrastructure_id}}"
         
         user: "{{metalcloud_user}}"
         api_key: "{{metalcloud_api_key}}"
         api_endpoint: "{{metalcloud_api_endpoint}}"  
```
## Pulling hosts and ssh credentials
```
---
- hosts: localhost
  vars: 
    infrastructure_label: "my-ansible-infra-11"
    
  tasks:
    - name: get credentials
      metalcloud_instance_array_instances: 
        infrastructure_label: "{{infrastructure_label}}"
        instance_array_label: "my-test"
        user: "{{metalcloud_user}}"
        api_key: "{{metalcloud_api_key}}"
        api_endpoint: "{{metalcloud_api_endpoint}}"
      register: haproxy
      no_log: true

    - name: add hosts
      add_host: 
        name: "{{item.instance_subdomain_permanent}}"
        ansible_ssh_port: "{{item.instance_credentials.ssh.port}}"
        ansible_ssh_user: "{{item.instance_credentials.ssh.username}}"
        #ansible_ssh_pass: "{{item.instance_credentials.ssh.initial_password}}"
        groups: "haproxy"
      with_items: "{{haproxy.instances}}"

- name: perform install
  hosts: haproxy
  tasks:
      - name: install haproxy
        yum: name=haproxy state=present
 ````
 
```


##
