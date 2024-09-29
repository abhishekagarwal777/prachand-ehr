import httpx
from typing import Optional, Union

class HttpClientConfig:
    def __init__(self, proxy: Optional[Union[str, None]] = None, proxy_port: int = 0):
        self.proxy = proxy
        self.proxy_port = proxy_port
        self.client = self.create_client()

    def create_client(self) -> httpx.Client:
        # Define proxy settings if applicable
        transport = httpx.HTTPTransport()
        if self.proxy and self.proxy_port:
            proxy_url = f"http://{self.proxy}:{self.proxy_port}"
            transport = httpx.HTTPTransport(proxy=proxy_url)

        # Create an HTTP client
        client = httpx.Client(
            http2=True,
            follow_redirects=False,
            timeout=20.0,
            transport=transport
        )

        return client

    def get_client(self) -> httpx.Client:
        return self.client

# Usage
http_client_config = HttpClientConfig(proxy="localhost", proxy_port=8080)
client = http_client_config.get_client()
