from .url_fetcher import UrlFetcher, CloudGwFetcher
from .fs_fetcher import LocalFetcher, FSCopyFetcher

def create_fetcher(method, app):
    if method == "cloud":
        return UrlFetcher(app)
    if method == "cloud_gw":
        return CloudGwFetcher(app)
    if method == "local":
        return LocalFetcher(app)
    if method == "fs":
        return FSCopyFetcher(app)
    raise Exception("No fetcher for method {}".format(method))

