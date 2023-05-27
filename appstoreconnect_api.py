import jwt
import requests
from uuid import UUID
from appstoreconnect_token_manager import AppStoreConnectTokenManager
from pydantic import BaseModel, parse_obj_as, validator
from typing import List

class AppStoreAppAttributes(BaseModel):
    name: str
    bundleId: str

class AppStoreApp(BaseModel):
    id: str
    attributes: AppStoreAppAttributes
    type: str
    
    @validator("type")
    def type_matches_type(cls, v):
        if v != "apps":
            raise ValueError(f"{cls} schema used with wrong API")
        return

class AppStoreBuildAttributes(BaseModel):
    version: str 

class AppStoreBuild(BaseModel):
    id: str
    attributes: AppStoreBuildAttributes
    type: str

    @validator("type")
    def type_matches_type(cls, v):
        if v != "builds":
            raise ValueError(f"{cls} schema used with wrong API")
        return

class AppStorePreReleaseVersionAttributes(BaseModel):
    version: str
    platform: str

class AppStorePreReleaseVersion(BaseModel):
    id: str
    attributes: AppStorePreReleaseVersionAttributes
    type: str

    @validator("type")
    def type_matches_type(cls, v):
        if v != "preReleaseVersions":
            raise ValueError(f"{cls} schema used with wrong API")
        return

class AppStoreVersionAttributes(BaseModel):
    versionString: str
    platform: str

class AppStoreVersion(BaseModel):
    id: str
    attributes: AppStoreVersionAttributes
    type: str

    @validator("type")
    def type_matches_type(cls, v):
        if v != "appStoreVersions":
            raise ValueError(f"{cls} schema used with wrong API")
        return

class AppStoreConnectAPI:
    BASE = "https://api.appstoreconnect.apple.com"

    def __init__(self):
        self.token_manager = AppStoreConnectTokenManager()

    def _api_version(self):
        return "v1"

    def _api_baseurl(self):
        return f"{self.BASE}/{self._api_version()}/"

    def get(self, path, params=None) -> dict:
        jwt = self.token_manager.get_token()
        r = requests.get(
            f"{self._api_baseurl()}{path}",
            params=params,
            headers={
                "Authorization": f"Bearer {jwt}",
            },
        )
        r.raise_for_status()
        return r.json()

    def get_latest_build_for_version(self, bundle_id, version_string: str, prerelease=True, platform="IOS") -> str:
        app = self.get_app(bundle_id)
        builds = []
        build_versions = []

        if app:
            versions = self.get_versions_for_app(app, prerelease)
            for version in versions:
                if prerelease:
                    if version.attributes.version == version_string and version.attribute.platform == platform:
                        builds = self.get_builds_for_version(version, prerelease)
                else:
                    if version.attributions.versionString == version_string and version.attribute.platform == platform:
                        builds = self.get_builds_for_version(version, prerelease)


            for build in builds:
                build_versions.append(build.attributes.version)
            if len(build_versions) > 0:
               return build_versions[0]
            if prerelease:
                print(f"Didn't find a prerelease version {version_string} for {bundle_id} on platform {platform}.")
            else:
                print(f"Didn't find a release version {version_string} for {bundle_id} on platform {platform}.")  
            return ""
 
    def get_latest_build(self, bundle_id, prerelease=True, for_version: str = None, platform="IOS") -> str:
        app = self.get_app(bundle_id)
        if app:
            version = self.get_latest_version_for_app(app, prerelease, platform)
            build_versions = []

            if version:
                builds = self.get_builds_for_version(version, prerelease)
                if builds:
                    for build in builds:
                        build_versions.append(int(build.attributes.version))
                    return max(build_versions)

            if prerelease:
                print(f"Didn't find a prerelease version for {bundle_id} on platform {platform}.")
            else:
                print(f"Didn't find a release version for {bundle_id} on platform {platform}.")
            return ""

    def get_latest_version(self, bundle_id, prerelease=True, platform="IOS") -> str:
        app = self.get_app(bundle_id)
        if app:
            version = self.get_latest_version_for_app(app, prerelease, platform)
            if version:
                return version

    def get_latest_version_for_app(self, app: AppStoreApp, prerelease=True, platform="IOS"):
        versions = self.get_versions_for_app(app, prerelease, platform)
        if prerelease:
            versions.sort(key=lambda x: x.attributes.version, reverse=True)
        else:
            versions.sort(key=lambda x: x.attributes.versionString, reverse=True)
        for version in versions:
            return version

    def get_versions_for_app(self, app: AppStoreApp, prerelease=True, platform="IOS"):
        if prerelease:
            appStoreData = self.get(f"apps/{app.id}/preReleaseVersions")["data"]
            versions = parse_obj_as(List[AppStorePreReleaseVersion], appStoreData)
        else:
            appStoreData = self.get(f"apps/{app.id}/appStoreVersions")["data"]
            versions = parse_obj_as(List[AppStoreVersion], appStoreData)
        return list(filter(lambda x: (x.attributes.platform == platform), versions))

    def get_builds_for_version(self, version: AppStoreVersion, prerelease=True):
        if prerelease:
            appStoreData = self.get(f"preReleaseVersions/{version.id}/builds")["data"]
            if appStoreData:
                builds = parse_obj_as(List[AppStoreBuild], appStoreData)
            else:
                builds = []
        else:
            appStoreData = self.get(f"appStoreVersions/{version.id}/build")["data"]
            if appStoreData:
                builds = [parse_obj_as(AppStoreBuild, appStoreData)]
            else:
                builds = []
        return builds

    def increment_ver(self, version: str) -> str:
        version = version.split('.')
        if len(version) > 1:
            version[len(version)-1] = str(int(version[2]) + 1)
            return '.'.join(version)
        else:
            return str(int(version[0])+1)

    def get_next_build(self, bundle_id, prerelease=True, platform="IOS") -> str:
        latest_build = self.get_latest_build(bundle_id, prerelease, platform=platform)
        if latest_build:
            return self.increment_ver(str(latest_build))

    def get_next_build_for_version(self, bundle_id, version: str, prerelease=True, platform="IOS") -> str:
        latest_build = self.get_latest_build_for_version(bundle_id, version, prerelease, platform=platform)
        if latest_build:
            return self.increment_ver(str(latest_build))

    def get_current_version(self, bundle_id, prerelease=True, platform="IOS") -> str:
        latest_version = self.get_latest_version(bundle_id, prerelease, platform=platform)
        if latest_version:
            if prerelease:
                return latest_version.attributes.version  
            else:         
                return latest_version.attributes.versionString 

    def get_app(self, bundle_id: str) -> list[dict]:
        # TODO handle paging
        apps = parse_obj_as(List[AppStoreApp], self.get("apps")["data"])
        for app in apps:
            if app.attributes.bundleId == bundle_id:
                return app

        print(f"App with bundle_id {bundle_id} not found.")
        return
