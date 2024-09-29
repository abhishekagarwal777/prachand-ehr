import ssl
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.auth import HTTPProxyAuth

class SSLAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.ssl_context
        return super().init_poolmanager(*args, **kwargs)

def create_http_client(properties):
    session = requests.Session()
    
    if properties['ssl']['enabled']:
        ssl_context = ssl.create_default_context()
        if properties['ssl']['key_store']:
            ssl_context.load_cert_chain(
                certfile=properties['ssl']['key_store'],
                keyfile=properties['ssl']['key_password']
            )
        if properties['ssl']['trust_store']:
            ssl_context.load_verify_locations(
                cafile=properties['ssl']['trust_store']
            )
        ssl_adapter = SSLAdapter(ssl_context=ssl_context)
        session.mount('https://', ssl_adapter)
    
    if properties['proxy']['host']:
        proxy_url = f"http://{properties['proxy']['host']}:{properties['proxy']['port']}"
        session.proxies.update({
            'http': proxy_url,
            'https': proxy_url
        })
        if properties['proxy']['username'] and properties['proxy']['password']:
            auth = HTTPProxyAuth(properties['proxy']['username'], properties['proxy']['password'])
            session.auth = auth
    
    return session

# Example usage:
properties = {
    'ssl': {
        'enabled': True,
        'key_store': 'path/to/keystore.pem',
        'key_password': 'your_key_password',
        'trust_store': 'path/to/truststore.pem'
    },
    'proxy': {
        'host': 'proxy.example.com',
        'port': 8080,
        'username': 'proxyuser',
        'password': 'proxypassword'
    }
}

http_client = create_http_client(properties)

# Now you can use `http_client` to make requests
response = http_client.get('https://example.com')
print(response.content)
