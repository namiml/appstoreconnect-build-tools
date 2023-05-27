#!/usr/bin/python3
import sys
import getopt
from appstoreconnect_api import AppStoreConnectAPI


if __name__ == "__main__":
    help_message = "get_latest_build.py [bundle_id] --version=[version] --platform=[IOS,TV_OS] --prerelease"

    prerelease_version = False
    version = None
    platform = "IOS"

    if len(sys.argv) < 2:
        print(help_message)
        sys.exit(2)

    bundle_id = sys.argv[1]
    appstore_api = AppStoreConnectAPI()

    try:
        opts, args = getopt.getopt(sys.argv[2:], "", ["prerelease", "version=", "platform="])
    except getopt.GetoptError:
        print(help_message)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("--prerelease"):
            prerelease_version = True
        if opt in ("--version="):
            version = arg
        if opt in ("--platform="):
            platform = arg

    if version:
        latest_build = appstore_api.get_latest_build_for_version(bundle_id, version, prerelease=prerelease_version, platform=platform)
    else:
        latest_build = appstore_api.get_latest_build(bundle_id, prerelease=prerelease_version, platform=platform)
    if latest_build:
        print(latest_build)
