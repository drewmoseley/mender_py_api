#!/usr/bin/env python3
#
import sys
import argparse
import menderAPI

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("device", help="Device ID or hostname on which to launch a shell")
    mender_api = menderAPI.MenderAPI(parser)
    
    matched_devices = mender_api.filtered_devices([mender_api.device_attribute("hostname", mender_api.args.device)])
    if len(matched_devices) > 1:
        sys.stderr.write("Multiple devices with hostname %s\n" % mender_api.args.device)
    elif len(matched_devices) == 1:
        mender_api.terminal(matched_devices[0]["id"])
    elif mender_api.device_with_id(mender_api.args.device) is not None:
        # The parameter is a device ID and not a hostname
        mender_api.terminal(mender_api.args.device)
    else:
        sys.stderr.write("No devices with hostname or device ID %s" % mender_api.args.device)

if __name__ == "__main__":
    sys.exit(main())
