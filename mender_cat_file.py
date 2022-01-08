#!/usr/bin/env python3
#
import sys
import argparse
import menderAPI

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("device", help="Device ID or hostname to download a file")
    parser.add_argument("path", help="Full path of the file to download")
    mender_api = menderAPI.MenderAPI(parser)

    matched_devices = mender_api.filtered_devices([mender_api.device_attribute("hostname", mender_api.args.device)])
    matched_device = None
    if len(matched_devices) > 1:
        sys.stderr.write("Multiple devices with hostname %s\n" % mender_api.args.device)
    elif len(matched_devices) == 1:
        matched_device = matched_devices[0]
    elif mender_api.device_with_id(mender_api.args.device) is not None:
        # The parameter is a device ID and not a hostname
        matched_device = mender_api.args.device
    else:
        sys.stderr.write("No devices with hostname or device ID %s" % mender_api.args.device)

    mender_api.cat_file(matched_device, mender_api.args.path)

if __name__ == "__main__":
    sys.exit(main())
