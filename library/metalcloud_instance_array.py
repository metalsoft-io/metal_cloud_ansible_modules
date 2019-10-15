#!/usr/bin/python

# Copyright: (c) 2018, Bigstep, inc


ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'bigstep'
}

DOCUMENTATION = '''
---
module: metalcloud_instance_array
short_description: create instance array
version_added: "1.0"
description:
    - create or edit an instance array.
    - parameters match instance_array_create function form the API
    - https://api.bigstep.com/metal-cloud#instance_array_create
    - https://api.bigstep.com/metal-cloud#instance_array_edit

options:

    user:
        description:
            - username
        required: true
    api_key:
        description:
            - api key
        required: true
    api_endpoint:
        description:
            - endpoint
        required: true
'''

EXAMPLES = '''
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

        user: "{{metalcloud_user}}"
        api_key: "{{metalcloud_api_key}}"
        api_endpoint: "{{metalcloud_api_endpoint}}"
      register: intance_array_1
'''

RETURN = '''
instance_array_id:
    - the instance array id of the created instance_array
'''

from ansible.module_utils.basic import AnsibleModule
from metal_cloud_sdk.clients.api import API
from jsonrpc2_base.plugins.client.signature_add import SignatureAdd


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        user = dict(type='str', required=True),
        api_key = dict(type='str', required=True),
        api_endpoint = dict(type='str', required=True),
 
        infrastructure_id = dict(type='int', required=True),
        instance_array_label = dict(type='str', required=True),
        drive_array_id_boot = dict(type='str', required=False, default=None),
        instance_array_boot_method= dict(type='str', required=False, default="pxe_iscsi"), 
        instance_array_instance_count = dict(type='int', required=False, default=1),
        instance_array_virtual_interfaces_enabled = dict(type='bool', required=False, default=False),
        instance_array_ipv4_subnet_create_auto = dict(type='bool', required=False, default=True),
        instance_array_ip_allocate_auto = dict(type='bool', required=False, default=True),
        instance_array_ram_gbytes = dict(type='int', required=False, default=1),
        instance_array_processor_count = dict(type='int', required=False, default=1),
        instance_array_processor_core_mhz = dict(type='int', required=False, default=1000),
        instance_array_processor_core_count = dict(type='int', required=False, default=1),
        instance_array_disk_count = dict(type='int', required=False, default=0),
        instance_array_disk_size_mbytes = dict(type='int', required=False, default=0),
        instance_array_firewall_rules = dict(type='list', required=False, default=[]),
        instance_array_firewall_managed = dict(type='bool', required=False, default=True),
        volume_template_id = dict(type='str', required=False, default=None)


   )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    print(module.__dict__.keys())

    mc_client = API.getInstance(
       {"strJSONRPCRouterURL": module.params['api_endpoint']},
       [SignatureAdd(module.params['api_key'], {})]
    )

    exists=False
    obj=mc_client.instance_arrays(module.params['infrastructure_id'])

    if type(obj) is dict:
            for k,v in obj.items():
              if v.instance_array_label==module.params['instance_array_label']:
                  exists=True
                  existing_obj=v
                  result['instance_array_id']=v.instance_array_id
                  break
   
    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        if(not exists): 
          result['message']='Instance array does not exist. Will create.' 
        module.exit_json(**result)

    keys=[k for k in module_args.keys() if k not in ['user','api_key','api_endpoint']]
    params = dict(zip(keys, [module.params[k] for k in keys]))
    
    if (not exists):
        obj=mc_client.instance_array_create(module.params['infrastructure_id'], params)
        result['changed'] = True
        result['instance_array_id']=obj.instance_array_id
    else:
        operation_obj=existing_obj.instance_array_operation
        for k in keys:
            if(k not in ['instance_array_boot_method','infrastructure_id']):
                old_v=getattr(operation_obj, k)
                if old_v != module.params[k]:
#                    print("changed key:"+k)
                    setattr(operation_obj, k, module.params[k])
                    result['changed'] = True
        
        obj=mc_client.instance_array_edit(existing_obj.instance_array_id, operation_obj)
        



    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
