#!/usr/bin/python
#
# Copyright (c) 2018  Krishna Kotha <krkotha@cisco.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
# This script retrieves entire interface configuration from a network element via RESTCONF

# import the requests library
import requests
import sys
import http.client
import ssl
import json
import base64

# curl -k "https://100.124.0.1:830/restconf/" -u "admin:admin"
# disable warnings from SSL/TLS certificates
# requests.packages.urllib3.disable_warnings()

# HOST = '100.127.100.20' # WLC
HOST = '100.124.0.1'  # Border
USER = 'admin'
PASS = 'admin'

cre = USER + ":" + PASS
credential_info = base64.b64encode(cre.encode('utf-8'))
credential_info = 'Basic ' + credential_info.decode('utf-8')

# create a main() method


def main():
    """Main method that retrieves the Interface details from Cat9300 via RESTCONF."""

    # url string to issue GET request
    # url = "https://{h}/restconf/data/ietf-interfaces:interfaces".format(h=HOST)
    url = "https://{h}/restconf/data/Cisco-IOS-XE-lldp-oper:lldp-entries".format(h=HOST)
    # url = "https://{h}/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage".format(h=HOST)

    # RESTCONF media types for REST API headers
    headers = {'Content-Type': 'application/yang-data+json',
               'Accept': 'application/yang-data+json',
               'Authorization': credential_info}

    # this statement performs a GET on the specified url

    conn = http.client.HTTPSConnection(
        HOST, context=ssl._create_unverified_context())

    conn.request("GET", url, headers=headers)
    res = conn.getresponse().read().decode("utf-8")
    lldp_state_details = json.loads(
        res)['Cisco-IOS-XE-lldp-oper:lldp-entries']['lldp-state-details']
    print(lldp_state_details)
    conn.close()


if __name__ == '__main__':
    sys.exit(main())
