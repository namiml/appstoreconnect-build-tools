#!/usr/bin/python3
import sys
import getopt
from appstoreconnect_api import AppStoreConnectAPI

if __name__ == "__main__":
    help_message = "get_next_build.py [bundle_id]"

    prelease_version = False

    if len(sys.argv) < 2:
        print(help_message)
        sys.exit(2)

    bundle_id = sys.argv[1]
    appstore_api = AppStoreConnectAPI()

    try:
        opts, args = getopt.getopt(sys.argv[2:], "", ["prerelease"])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("--prerelease"):
            prelease_version = True

    next_build = appstore_api.get_next_build(bundle_id, prerelease=prelease_version)
    if next_build:
        print(next_build)