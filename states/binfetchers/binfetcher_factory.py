from .url_fetcher import UrlFetcher, CloudGwFetcher

def create_fetcher(method, app):
    if method == "cloud":
        return UrlFetcher(app)
    if method == "cloud_gw":
        return CloudGwFetcher(app)
    raise Exception("No fetcher for method {}".format(method))

