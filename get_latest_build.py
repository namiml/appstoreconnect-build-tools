#!/usr/bin/python3
import sys
import getopt
from appstoreconnect_api import AppStoreConnectAPI


if __name__ == "__main__":
    help_message = "get_latest_build.py [bundle_id]"

    prerelease_version = False
    version = None

    if len(sys.argv) < 3:
        print(help_message)
        sys.exit(2)

    bundle_id = sys.argv[1]
    appstore_api = AppStoreConnectAPI()

    try:
        opts, args = getopt.getopt(sys.argv[2:], "", ["prerelease", "version="])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    print(opts)
    for opt, arg in opts:
        if opt in ("--prerelease"):
            prerelease_version = True
        elif opt in ("--version="):
            version = arg

    if version:
        latest_build = appstore_api.get_latest_build_for_version(bundle_id, version, prerelease=prerelease_version)
    else:
        latest_build = appstore_api.get_latest_build(bundle_id, prerelease=prerelease_version)
    if latest_build:
        print(latest_build)
