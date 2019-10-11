#!/usr/bin/python

# Copyright: (c) 2018, Bigstep, inc

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'bigstep'
}

DOCUMENTATION = '''
---
module: metalcloud_instance_array_instances
short_description: returns details and credentials of the instances part of an instance array
version_added: "1.0"
description:
    - return instances details including credentials

options:
    instance_array_id:
        description:
            - instance array id. If this is defined infrastructure_label and instance_array_label must not be used.
        required: false
    infrastructure_label:
        description:
            - infrastructure label
        required: false
    instance_array_label:
        description:
            - instance array label
        required: false
    
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
# Pass in a message
 - name: get credentials
      metalcloud_instance_array_instances: 
        infrastructure_label: "{{infrastructure_label}}"
        instance_array_label: "my-test"
        user: "{{metalcloud_user}}"
        api_key: "{{metalcloud_api_key}}"
        api_endpoint: "{{metalcloud_api_endpoint}}"
      register: haproxy
      no_log: true
'''

RETURN = '''
instances:
        instance_credentials:
            ssh:
                username
                initial_password
                port
        instance_id
        instance_label
        instance_service_status
        instance_subdomain
        instance_subdomain_permanent
        server_type_id
'''

from ansible.module_utils.basic import AnsibleModule
from metal_cloud_sdk.clients.api import API
from jsonrpc2_base.plugins.client.signature_add import SignatureAdd
import time

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        user=dict(type='str', required=True),
        api_key=dict(type='str', required=True),
        api_endpoint=dict(type='str', required=True),
 
        instance_array_id=dict(type='int', required=False, deafult=None),
        infrastructure_label=dict(type='str', required=False, default=None),
        instance_array_label=dict(type='str', required=False, default=None),
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
        supports_check_mode=False
    )

    if (module.params['instance_array_id']!=None): 
        if(module.params['infrastructure_label']!=None or module.params['instance_array_label']!=None):
           raise BaseException("if instance_array_id is defined infrastructure_label and instance_array_label cannot be used")
    else:
        if(module.params['infrastructure_label']==None or module.params['instance_array_label']==None):
           raise BaseException("if instance_array_id is null infrastructure_label and instance_array_label must be defined")   

    mc_client = API.getInstance(
       {"strJSONRPCRouterURL": module.params['api_endpoint']},
       [SignatureAdd(module.params['api_key'], {})]
    )

    instances = None

    if(module.params['instance_array_id']!=None):
        instances=mc_client.instance_array_instances(module.params['instance_array_id'])
    else:
        obj=mc_client.instance_arrays(module.params['infrastructure_label'])
        if type(obj) is dict:
            for k,v in obj.items():
              if v.instance_array_label==module.params['instance_array_label']:
                  instance_array_id=v.instance_array_id
                  instances=mc_client.instance_array_instances(instance_array_id)
                  break

    if(instances is None):
        raise BaseException('instance_array not found')

    #build credentials object

    ret_obj=[]
    for k,v in instances.items():
        ret_obj.append({
            'instance_label': v.instance_label,
            'instance_id': v.instance_id,
            'instance_subdomain': v.instance_subdomain,
            'instance_subdomain_permanent':v.instance_subdomain_permanent,
            'server_type_id':v.server_type_id,
            'instance_service_status':v.instance_service_status,
            'instance_credentials':
                {'ssh':
                    {
                        'port':v.instance_credentials.ssh.port,
                        'username': v.instance_credentials.ssh.username,
                        'initial_password':v.instance_credentials.ssh.initial_password
                    }
                }
        })
       #ret_obj.append(v.instance_subdomain_permanent)
    result['instances'] = ret_obj

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
