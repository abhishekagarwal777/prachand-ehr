from datetime import datetime, timezone
from flask import g
from flask import Flask
from EhrServiceImp import RequestScopedTimeProvider

app = Flask(__name__)

class TimeProvider:
    def get_now(self) -> datetime:
        pass

class RequestScopedTimeProvider(TimeProvider):
    def __init__(self):
        self.now = None

    def init(self):
        self.now = datetime.now(timezone.utc)

    def get_now(self) -> datetime:
        return self.now


class RequestScopedTimeProvider:
    def get_time(self):
        # Implementation here
        pass

def request_scoped_time_provider() -> RequestScopedTimeProvider:
    return RequestScopedTimeProvider()

time_provider = request_scoped_time_provider()
current_time = time_provider.get_time()



@app.before_request
def before_request():
    time_provider = RequestScopedTimeProvider()
    time_provider.init()
    g.request_scoped_time_provider = time_provider

@app.route('/current_time')
def current_time():
    return {'current_time': g.request_scoped_time_provider.get_now().isoformat()}



from typing import Any

class RequestScopedTimeProvider:
    def get_time(self):
        # Implementation here (e.g., return current time)
        import datetime
        return datetime.datetime.now()

def request_scoped_time_provider() -> Any:
    return RequestScopedTimeProvider()

provider = request_scoped_time_provider()
current_time = provider.get_time()
print("Current Time:", current_time)
