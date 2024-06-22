from pachca_client.api.pachca import Pachca
from pachca_client.api.client import Client
from pachca_client.api.cache import Cache
from pachca_client.api.file import File

def get_pachca(access_token: str, cache_enabled: bool = True) -> Pachca:
    client = Client(access_token)
    cache = None
    if cache_enabled:
        cache = Cache()

    return Pachca(client, cache)