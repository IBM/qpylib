# Changelog

## 2.0.1
- Non-SDK REST calls default to `verify=True`.  
SDK default remains `verify=False` for now, but that will change in a future release.

## 2.0
- First official release of qpylib on Github.
- Support for Python 3 and Red Hat UBI app base image.
- abstract/sdk/live layers removed.
- New encryption algorithm in encdec.py, plus backwards compatibility with previous versions.
- New ariel.py module supports Ariel searches via REST API.
- `get_app_id` now uses `QRADAR_APP_ID` environment variable instead of manifest value.
- REST methods now pass through `kwargs`.
- REST replaces `gethostname()` with `localhost`.