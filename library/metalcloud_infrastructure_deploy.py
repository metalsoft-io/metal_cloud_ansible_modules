#!/usr/bin/python

# Copyright: (c) 2018, Bigstep, inc

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'bigstep'
}

DOCUMENTATION = '''
---
module: metalcloud_infrastructure_deploy
short_description: deploy an infrastructure
version_added: "1.0"
description:
    - deploys an infrastructure
    - parameters match infrastructure_deploy function form the API
    - https://api.bigstep.com/metal-cloud#infrastructure_deploy

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
# Pass in a message
 - name: deploy changes if needed.
      metalcloud_infrastructure_deploy:
         infrastructure_id: "{{infrastructure.infrastructure_id}}"
         
         user: "{{metalcloud_user}}"
         api_key: "{{metalcloud_api_key}}"
         api_endpoint: "{{metalcloud_api_endpoint}}"
'''

RETURN = '''
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
 
        infrastructure_id=dict(type='int', required=True),
        shutdown_options=dict(type='dict', required=False, default=None),
        deploy_options=dict(type='dict', required=False, default=None),
        allow_data_loss=dict(type='bool', required=False, default=False),
        skip_ansible=dict(type='bool', required=False, default=False),
        
        wait_for_deploy=dict(type='bool', required=False, default=True),
        wait_timeout=dict(type='int', required=False, default=60*60),

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

    mc_client = API.getInstance(
       {"strJSONRPCRouterURL": module.params['api_endpoint']},
       [SignatureAdd(module.params['api_key'], {})]
    )

    keys=[k for k in module_args.keys() if k not in ['user','api_key','api_endpoint', 'wait_for_deploy','wait_timeout']]
    params = dict(zip(keys, [module.params[k] for k in keys]))
    
    obj = mc_client.infrastructure_get(module.params['infrastructure_id'])

    #if there are pending operations
    if(obj.infrastructure_operation.infrastructure_deploy_status=="not_started"):
        mc_client.infrastructure_deploy(
            module.params['infrastructure_id'], 
            module.params['shutdown_options'],
            module.params['deploy_options'],
            module.params['allow_data_loss'],
            module.params['skip_ansible'])

    
        if(module.params['wait_for_deploy']):
            timeout = time.time() + module.params['wait_timeout']   # 5 minutes from now
            while True:
                obj = mc_client.infrastructure_get(module.params['infrastructure_id'])
                if obj.infrastructure_operation.infrastructure_deploy_status=='finished':
                    break
                if time.time() < timeout:
                    time.sleep(30)
                else:
                    raise BaseException("Deploy ongoing for more than "+str(module.params['wait_timeout'])+" seconds")

        result['changed'] = True


    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
