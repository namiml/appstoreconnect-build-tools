#!/usr/bin/python3
import sys
import time
import getopt
from appstoreconnect_api import AppStoreConnectAPI


if __name__ == "__main__":
    help_message = "upload_testflight_whats_new.py [bundle_id] --notes=[whats_new] --version=[version] --platform=[IOS,TV_OS] --prerelease"

    whats_new = None
    prerelease_version = False
    version = None
    platform = "IOS"

    if len(sys.argv) < 3:
        print(help_message)
        sys.exit(2)

    bundle_id = sys.argv[1]
    whats_new = sys.argv[2]
    appstore_api = AppStoreConnectAPI()

    try:
        opts, args = getopt.getopt(sys.argv[3:], "", ["prerelease", "notes=", "version=", "platform="])
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
        if opt in ("notes="):
            whats_new = arg

    error = False

    if whats_new is None:
        print("upload_testflight_whats_new.py: --notes=[whats_new] is missing")
        error = True    
    if prerelease_version is False:
        print("upload_testflight_whats_new.py: this script is for pre-release testflight builds only ")
        error = True
    
    retries = 5
    
    if error is False:
        for retry in range(retries):
            if version:
                latest_build_obj = appstore_api.get_latest_build_obj_for_version(bundle_id, version, prerelease=prerelease_version, platform=platform)
            else:
                latest_build_obj = appstore_api.get_latest_build_obj(bundle_id, prerelease=prerelease_version, platform=platform)
            if latest_build_obj:
                if latest_build_obj.attributes.processingState != "VALID":
                    print("ERROR: TestFlight build is still processing...is for pre-release testflight builds only")
                    time.sleep(60)
                else:
                    response = appstore_api.upload_testflight_whats_new(latest_build_obj.id, whats_new)
                    if response.status_code == 201:
                        print (f"What's new upload successful for build {latest_build_obj.attributes.version}")
                        break
                    else:
                        print (f"What's new upload failed for build {latest_build_obj.attributes.version}\nstatus {response.status_code} - {response.json()}")
                        break
            else:
                print("Did not find a build id, release notes not updated")
                break

        print (f"What's new upload failed after 5 retries")                        
