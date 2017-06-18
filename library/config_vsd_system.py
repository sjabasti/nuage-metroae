#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import importlib
from bambou import exceptions

VSPK = None

DOCUMENTATION = '''
---
module: config_vsd_system
short_description: Update/configure VSD System parameters
options:
  vsd_auth:
    description:
      - VSD credentials to access VSD GUI
    required: true
    default: null
  gateway_purge_time:
    description:
      - Increase or decrease timeout value in VSD
    default: null
  get_gateway_purge_time:
    decription:
      - Get the current gateway purge tiem set
    default: False
    choices: [ True, False ]
  api_version:
    description:
      - VSD version
    required: true
    default: null

'''

EXAMPLES = '''
# Configure gateway purge time in VSD
- config_vsd_system:
    vsd_auth:
      username: csproot
      password: csproot
      enterprise: csp
      api_url: https://10.0.0.10:8443
    gateway_purge_time: 7003
    api_version: 4.0.R8

- config_vsd_system:
    vsd_auth:
      username: csproot
      password: csproot
      enterprise: csp
      api_url: https://10.0.0.10:8443
    get_gateway_purge_time: True
    api_version: 4.0.R8
'''


def format_api_version(version):
    # Handle 3.2 seperately
    if version.startswith('3'):
        return ('v3_2')
    else:
        return ('v' + version[0] + '_0')


def get_vsd_session(vsd_auth):
    # Format api version
    version = format_api_version(module.params['api_version'])
    try:
        global VSPK
        VSPK = importlib.import_module('vspk.{0:s}'.format(version))
    except ImportError:
            module.fail_json(msg='vspk is required for this module, or\
                             API version specified does not exist.')

    try:
        session = VSPK.NUVSDSession(**vsd_auth)
        session.start()
        csproot = session.user
        return csproot
    except:
        module.exit_json(changed=False, result="Could not establish\
                          connection to VSD")


def set_gateway_purge_time(csproot, gw_purge_time):
    try:
        sys_config = csproot.system_configs.get_first()
        sys_config.ad_gateway_purge_time = int(gw_purge_time)
        sys_config.save()
    except exceptions.BambouHTTPError as e:
        if "There are no attribute changes" in e.message:
            module.exit_json(changed=True, result="Gateway time is already\
                             updated to %s" % int(gw_purge_time))
    except Exception as e:
        module.fail_json(msg="Could not update\
                         gateway purge timer : %s" % e)

    module.exit_json(changed=True,
                     result="Gateway purge time set to %ssec" % gw_purge_time)


def get_gateway_purge_time_value(csproot):
    try:
        sys_config = csproot.system_configs.get_first()
        purge_val = sys_config.ad_gateway_purge_time
    except Exception as e:
        module.fail_json(msg="Could not retrieve\
                         gateway purge timer : %s" % e)
    module.exit_json(changed=True,
                     result=purge_val)

arg_spec = dict(
    vsd_auth=dict(required=True, type='dict'),
    api_version=dict(required=True, type='str'),
    get_gateway_purge_time=dict(default=False, type='bool'),
    gateway_purge_time=dict(type='int')
)
module = AnsibleModule(argument_spec=arg_spec, supports_check_mode=True)


def main():
    vsd_auth = module.params['vsd_auth']
    gw_purge_time = module.params['gateway_purge_time']
    get_gateway_purge_time = module.params['get_gateway_purge_time']
    csproot = get_vsd_session(vsd_auth)

    if not get_gateway_purge_time:
        set_gateway_purge_time(csproot, gw_purge_time)
    else:
        get_gateway_purge_time_value(csproot)


main()
