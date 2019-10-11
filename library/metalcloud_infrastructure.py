#!/usr/bin/python

# Copyright: (c) 2018, bigstep, inc
ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'bigstep'
}

DOCUMENTATION = '''
---
module: metalcloud_infrastructure
short_description: create infrastructures
version_added: "1.0"
description:
    - create infrastructure

options:
    infrastructure_label:
        description:
            - Create infrastructures and register infrastructure ids into the variables
        required: true

    datacenter_name: 
        description:
            - Where to create the infrastructure
        required: true

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
 - name: create a blank infrastructure
      metalcloud_infrastructure: 
        infrastructure_label: "test"
        datacenter_name: 'uk-reading'
        user: "test@test.com"
        api_key: "test"
        api_endpoint: "https://api.bigstep.com/metal-cloud"
      register: infrastructure
'''

RETURN = '''
infrastructure_id:
    description: The infrastructure id
    type: int
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from metal_cloud_sdk.clients.api import API
from jsonrpc2_base.plugins.client.signature_add import SignatureAdd


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        infrastructure_label=dict(type='str', required=True),
        datacenter_name=dict(type='str', required=True),
        user=dict(type='str', required=True),
        api_key=dict(type='str', required=True),
        api_endpoint=dict(type='str', required=False, default="https://api.bigstep.com/metal-cloud" )
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        #original_message='',
        #message='',
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    mc_client = API.getInstance(
       {"strJSONRPCRouterURL": module.params['api_endpoint']},
       [SignatureAdd(module.params['api_key'], {})]
    )

    obj = mc_client.infrastructures(module.params['user']) 

    exists = False
    if type(obj) is dict:
            for k,v in obj.items():
              if v.infrastructure_label==module.params['infrastructure_label']:
                  exists=True
                  existing_obj=v
                  result['infrastructure_id']=v.infrastructure_id
                  break

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        if(not exists):
          result['message']='Infrastructure does not exist. Will create' 
        module.exit_json(**result)


    if (not exists):
        params={
          "infrastructure_label": module.params['infrastructure_label'],
          "datacenter_name": module.params['datacenter_name'] 
        }
        obj = mc_client.infrastructure_create(module.params['user'], params)
        result['infrastructure_id']=obj.infrastructure_id
        result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
