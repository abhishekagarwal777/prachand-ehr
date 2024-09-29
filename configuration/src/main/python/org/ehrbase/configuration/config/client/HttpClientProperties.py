from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Proxy:
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None

@dataclass
class Ssl:
    enabled: bool = False
    key_password: Optional[str] = None
    key_store: Optional[str] = None
    key_store_password: Optional[str] = None
    key_store_type: Optional[str] = None
    trust_store: Optional[str] = None
    trust_store_password: Optional[str] = None
    trust_store_type: Optional[str] = None

@dataclass
class HttpClientProperties:
    proxy: Proxy = field(default_factory=Proxy)
    ssl: Ssl = field(default_factory=Ssl)

# Example usage:
properties = HttpClientProperties(
    proxy=Proxy(
        host='proxy.example.com',
        port=8080,
        username='proxyuser',
        password='proxypassword'
    ),
    ssl=Ssl(
        enabled=True,
        key_store='path/to/keystore.pem',
        key_password='key_password',
        trust_store='path/to/truststore.pem',
        trust_store_password='truststore_password'
    )
)

print(properties)
