#!/usr/bin/python3
import sys
import getopt
from appstoreconnect_api import AppStoreConnectAPI


if __name__ == "__main__":
    help_message = "get_current_version.py [bundle_id] --prerelease --platform=[IOS,TV_OS]"

    prelease_version = False
    platform = "IOS"

    if len(sys.argv) < 2:
        print(help_message)
        sys.exit(2)

    bundle_id = sys.argv[1]
    appstore_api = AppStoreConnectAPI()

    try:
        opts, args = getopt.getopt(sys.argv[2:], "", ["prerelease", "platform="])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("--prerelease"):
            prelease_version = True
        if opt in ("--platform="):
            platform = arg
    latest_build = appstore_api.get_current_version(bundle_id, prerelease=prelease_version, platform=platform)
    if latest_build:
        print(latest_build)
