from ncclient import manager
import xmltodict
import re

# host = '100.127.100.20' # WLC
host = '100.124.0.1' #Border1
port = 830
username = 'opas'
password = 'Cisco!23'

# eos=manager.connect(host=host, port=port, username=username, password=password, hostkey_verify=False)
# eos.connected
# eos.get_config(source='running').data_xml
# eos.close_session()

with manager.connect(host=host, port=port, username=username, password=password, hostkey_verify=False) as m:
    c = m.get_config(source='running').data_xml
    # with open("%s.xml" % host, 'w') as f:
    #     f.write(c)
    # result = xmltodict.parse(c)

    capabilities = []
    # Write each capability to console
    for capability in m.server_capabilities:
        # Print the capability
        # print("Capability: %s" % capability)
        # Store the capability list for later.
        capabilities.append(capability)

    # Sort the list alphabetically.
    capabilities = sorted(capabilities)

    # List of modules that we store for use later
    modules = []

    # Iterate server capabilities and extract supported modules.
    for capability in capabilities:
        # Scan the capabilities and extract modules via this regex.
        # i.e., if this was the capability string:
        #   http://www.cisco.com/calvados/show_diag?module=show_diag&revision=2012-03-27
        # then:
        #   show_diag
        # .. would be the module printed.
        # Scan capability string for module
        supported_model = re.search('module=(.*)&', capability)
        # If module found in string, store it.
        if supported_model is not None:
            # Module string was found, store it.
            # print("Supported Model: %s" % supported_model.group(1))
            # Store the module for later use.
            modules.append(supported_model.groups(0)[0])


    # List of models that we want to download.
    # We will get the schema for each and write it to disk.
    # models_desired = ['openconfig-extensions', 'openconfig-interfaces']
    models_desired = ['Cisco-IOS-XE-process-cpu-oper']

    # Iterate each desired model and write it to ./lab/models/
    for model in models_desired:
        # Get the model schema.
        schema = m.get_schema(model)
        # Open new file handle.
        with open("{}.yang".format(model), 'w') as f:
            # Write schema
            f.write(schema.data)
    


