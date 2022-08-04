# appstoreconnect-build-tools

A simple Python 3 CLI for interacting with the App Store Connect API to get build and version information. Includes a tool determine the next expected build version for both App Store and TestFlight pre-release versions.

## Prerequisites

* Python 3
* pydantic
    - `pip3 install pydantic`
* requests
    - `pip3 install requests`
* cryptography
    - `pip3 install cryptography`
* PyJWT
    - `pip3 install PyJWT`   
   
## Set environment variables

All credential details for the App Store Connect API are read in from environment variables:

`export APPSTORE_ISSUER_ID=<issuer id>`
`export APPSTORE_API_KEY_ID=<key id>`
`export APPSTORE_API_PRIVATE_KEY=<private key>`

## Usage examples

### Get current App Store version for a bundle ID

```
python3 get_current_version.py [bundle_id]
```

### Get latest App Store build number for a bundle ID

```
python3 get_latest_build.py [bundle_id]
```

### Get next expected App Store build number for a bundle ID
```
python3 get_next_build.py [bundle_id] --prerelease
```

### Get current prerelease version for a bundle ID

```
python3 get_current_version.py [bundle_id] --prerelease
```

### Get latest prerelease build number for a bundle ID

```
python3 get_latest_build.py [bundle_id] --prerelease
```
### Get next expected prerelease build number for a bundle ID

```
python3 get_next_build.py [bundle_id] --prerelease
```

