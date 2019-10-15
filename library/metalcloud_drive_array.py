#!/usr/bin/python

# Copyright: (c) 2018, bigstep, inc
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
---
module: metalcloud_instance_array
short_description: create instance array
version_added: "1.0"
description:
    - create or edit drive array.
    - parameters match drive_array_create and  drive_array_edit functions form the api
    https://api.bigstep.com/metal-cloud#drive_array_create
    https://api.bigstep.com/metal-cloud#drive_array_edit

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
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule
from metal_cloud_sdk.clients.api import API
from jsonrpc2_base.plugins.client.signature_add import SignatureAdd


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        user=dict(type='str', required=True),
        api_key=dict(type='str', required=True),
        api_endpoint=dict(type='str', required=True),
        infrastructure_id=dict(type='int', required=True),
        instance_array_id=dict(type='int', required=True),
        drive_array_label=dict(type='str', required=True),
        volume_template_label=dict(type='str', required=True),
        drive_array_storage_type=dict(type='str', required=False, default='iscsi_ssd'),
        drive_array_count=dict(type='int', required=False, default=1),
        drive_size_mbytes_default=dict(type='int', required=False, default=40960)
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

    mc_client = API.getInstance(
       {"strJSONRPCRouterURL": module.params['api_endpoint']},
       [SignatureAdd(module.params['api_key'], {})]
    )

    exists=False
    obj=mc_client.drive_arrays(module.params['infrastructure_id'])

    if type(obj) is dict:
       for k,v in obj.items():
          if v.drive_array_label==module.params['drive_array_label']:
             exists=True
             existing_obj=v
             break
     # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        if(not exists): 
          result['message']='Drive array does not exist. Will create' 
        module.exit_json(**result)

   #locate the exact volume template 
    volume_template_id=0
    obj=mc_client.volume_templates(module.params['user'])
    if type(obj) is dict:
        for k,v in obj.items():
          if v.volume_template_label==module.params['volume_template_label']:
              volume_template_id=v.volume_template_id
              break

    if(volume_template_id is 0):
        raise BaseException('volume template '+module.params['volume_template_label']+' not found')

    #get all params
    keys=[k for k in module_args.keys() if k not in ['user','api_key','api_endpoint','instance_array_label','infrastructure_label','volume_template_label']]
    params = dict(zip(keys, [module.params[k] for k in keys]))
    

    if (not exists):
      params['volume_template_id']=volume_template_id
      mc_client.drive_array_create(module.params['infrastructure_id'], params)
      result['changed'] = True
    else:
        operation_obj=existing_obj.drive_array_operation
        for k in keys:
                old_v=getattr(operation_obj, k)
                if old_v != module.params[k]:
                    print("changed key:"+k+" old val="+str(old_v)+" new val="+str(module.params[k]))

                    setattr(operation_obj, k, module.params[k])
                    result['changed'] = True

        if(operation_obj.volume_template_id != volume_template_id):
            result['changed'] = True
            operation_obj.volume_template_id = volume_template_id

        print(operation_obj.instance_array_id)

        obj=mc_client.drive_array_edit(existing_obj.drive_array_id, operation_obj)
    

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
#    result['original_message'] = module.params['']
 #   result['message'] = 'goodbye'

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    #if module.params['fail_if_exists']:

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
 #   if module.params['name'] == 'fail me':
 #       module.fail_json(msg='You requested this to fail', **result)



    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
