class PreconditionFailedException(RuntimeError):
    def __init__(self, message: str, current_version_uid: str = None, url: str = None):
        super().__init__(message)
        self._current_version_uid = current_version_uid
        self._url = url

    @property
    def current_version_uid(self):
        return self._current_version_uid

    @property
    def url(self):
        return self._url


def check_condition(version_uid, url):
    if not version_uid or not url:
        raise PreconditionFailedException(
            "Precondition failed",
            current_version_uid=version_uid,
            url=url
        )

try:
    check_condition(None, "http://example.com")
except PreconditionFailedException as e:
    print(f"Exception: {e}, Version UID: {e.current_version_uid}, URL: {e.url}")
