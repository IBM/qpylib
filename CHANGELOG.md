# Changelog

## 2.0.6
- Fix missing `util_qpylib` missing from `qpylib` parent module.

## 2.0.5
- SDK rest calls now default to verify=True rather than verify=False.
- Add protection against multiple calls of create_log().
- Add create_log() flag to enable/disable SysLogHandler.

## 2.0.4
- Update cryptography package version to address security vulnerabilities.

## 2.0.3
- Freeze pip requirements.
- Add wheel generation.

## 2.0.2
- Log handling changes.
- Cancel and delete functions added to `ariel.py` module.

## 2.0.1
- Non-SDK REST calls default to `verify=True`.
SDK default remains `verify=False` for now, but that will change in a future release.

## 2.0
- First official release of qpylib on Github.
- Support for Python 3 and Red Hat UBI app base image.
- abstract/sdk/live layers removed.
- New encryption algorithm in `encdec.py`, plus backwards compatibility with previous algorithms.
All `encdec` error-handling is now performed using `encdec.EncryptionError`.
- New `ariel.py` module supports Ariel searches via REST API.
- `get_app_id` now uses `QRADAR_APP_ID` environment variable instead of manifest value.
- REST methods now pass through `kwargs`.
- `REST` now uses `localhost` instead of `gethostname()`.
- Functions with changed parameter names: `get_root_path`, `get_store_path`, `REST`.
