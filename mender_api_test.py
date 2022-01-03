#!/usr/bin/env python3
#

""" Basic Test app for the menderAPI class """

import sys
import menderAPI

def print_device_identity_fields(device):
    print("id = %s" % device["id"])
    for field in filter(lambda f: f["scope"] == "identity", device["attributes"]):
        print("\t%s = %s" % (field["name"], field["value"]))

def print_device_hostname(device):
    print("id = %s" % device["id"])
    for field in filter(lambda f: f["name"] == "hostname", device["attributes"]):
        print("\t%s = %s" % (field["name"], field["value"]))

def main():
    ''' Main method of Test app for the menderAPI class '''
    mender_api = menderAPI.MenderAPI()
    mender_api.for_all_devices(print_device_identity_fields)
    mender_api.for_all_devices(print_device_hostname)

if __name__ == "__main__":
    sys.exit(main())
