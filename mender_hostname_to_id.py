#!/usr/bin/env python3
#
import sys
import menderAPI
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", help="Hostname to map to an ID")
    mender_api = menderAPI.MenderAPI(parser)
    for device in mender_api.filtered_devices([mender_api.device_attribute("hostname", mender_api.args.hostname)]):
        print(device["id"])

if __name__ == "__main__":
    sys.exit(main())
