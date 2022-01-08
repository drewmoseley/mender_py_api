#
# Library for accessing the Mender API
#

import argparse
import os
import sys
import json
import getpass
import tempfile
import requests

class MenderAPI:
    ''' Wrapper class for the Mender API '''

    def __init__(self, parser=None):
        self.args = None
        self.__devices = None
        self.num_api_calls = 0
        self.parser = parser or argparse.ArgumentParser()
        self.parser.add_argument("--server",
                                 help="URL of the Mender server to use",
                                 default="https://hosted.mender.io")
        self.parser.add_argument("--username",
                                 help="Email address of the user to connect to the Mender server",
                                 required=True)
        self.parser.add_argument("--password",
                                 help="Password used to log into the Mender server")
        self.parser.add_argument("--jwt",
                                 help="The JWT to use to connect to the Mender server",
                                 default=os.environ.get("JWT"))
        self.parser.add_argument("--stats",
                                 help="Print statistics at the end of invocation",
                                 dest="stats", action="store_true")
        self.args = self.parser.parse_args()

        if self.args.jwt is None:
            # Authenticate using a password
            if self.args.password is None:
                self.args.password = getpass.getpass(prompt='Mender Server Password: ', stream=None)
            self.args.jwt = self.api_post("management/v1/useradm/auth/login").text
        elif self.args.password is not None:
            sys.stderr.write("Warning. Both JWT and password are specified. Ignoring the password.")
            self.args.password = None

    def __del__(self):
        if self.args and self.args.stats:
            sys.stderr.write("Total calls to Mender server API: %d\n" % self.num_api_calls)
        if os.environ.get("JWT") is None and self.args is not None and self.args.jwt is not None:
            sys.stderr.write("Make sure to set the JWT environment variable to avoid\n")
            sys.stderr.write("reauthenticating to the Mender server for future command\n")
            sys.stderr.write("invocations\n\n")
            sys.stderr.write("export JWT=%s\n" % self.args.jwt)

    def __api_call(self, operation, api_substring, params, return_type):
        ''' Send an API get or post call'''
        if self.args.jwt is None:
            headers = {
                'Accept': return_type,
            }
            auth=(self.args.username, self.args.password)
        else:
            headers = {
                'Accept': return_type,
                'Authorization': 'Bearer %s' % self.args.jwt
            }
            auth=None

        try:
            self.num_api_calls += 1
            req = operation("%s/api/%s" % (self.args.server, api_substring),
                            data="", auth=auth, headers=headers, params=params)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        return req

    def api_post(self, api_substring, params = None, return_type = "application/json"):
        ''' Send a post API request to the server '''
        return self.__api_call(requests.post, api_substring, params, return_type)

    def api_get(self, api_substring, params = None, return_type = "application/json"):
        ''' Send a get API request to the server '''
        return self.__api_call(requests.get, api_substring, params, return_type)

    def devices(self):
        ''' Enumerate the device list from the server'''
        if self.__devices is None:
            self.__devices = json.loads(self.api_get("management/v1/inventory/devices").text)
        return self.__devices

    def __match(self, device, filterAttributes):
        for attribute in filterAttributes:
            if attribute not in device["attributes"]:
                return False
            return True

    def device_with_id(self, device_id):
        ''' Return a single device with a specific ID '''
        return [ d for d in self.devices() if d["id"] == device_id ]

    def filtered_devices(self, client_side_filter=None):
        ''' Return the device list with an optional client-side filter'''
        return [ d for d in self.devices() if self.__match(d, client_side_filter)]
    
    def for_all_devices(self, func):
        ''' Invoke func over all devices '''
        return list(map(func, self.devices()))

    def device_attribute(self, name, value, scope="inventory"):
        ''' Create a device attribute dict from the basic values '''
        return {"name": name, "value": value, "scope": scope}

    def terminal(self, device_id):
        ''' Launch a shell terminal on the device using mender-cli '''
        with tempfile.NamedTemporaryFile(mode='wt') as jwt_file:
            jwt_file.write(self.args.jwt)
            jwt_file.flush()
            os.system("mender-cli --server %s --token %s terminal %s" % (self.args.server, jwt_file.name, device_id))
