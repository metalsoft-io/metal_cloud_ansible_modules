from metal_cloud_sdk.clients.api import API
from jsonrpc2_base.plugins.client.signature_add import SignatureAdd



def get_client(api_key, endpoint='https://fullmetal.bigstep.com/api'):
    return API.getInstance(
            {
              "strJSONRPCRouterURL": endpoint
             },
            [
                SignatureAdd(api_key, {})
#                DebugLogger(True, "DebugLogger.log")
            ]
        )

def infrastructure_exists(api_client, user, infrastructure_label):
      obj=api_client.infrastructures(user) 
      return infrastructure_label in obj



def create_infrastructure(api_client, user, infrastructure_label, datacenter_name):
    params={
      "infrastructure_label":infrastructure_label,
      "datacenter_name": datacenter_name
    }

    return api_client.infrastructure_create(user, params)



