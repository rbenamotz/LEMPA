import urllib.request
import requests
from pathlib import Path
from states.binfetchers import BinFetcher


class UrlFetcher(BinFetcher):
    def __fetch_impl__(self, bin_info, bin_file):
        self.app.print("DL {}".format(bin_file))
        if "url" not in bin_info:
            raise Exception("Missing URL for bin")
        download_url = bin_info["url"]
        self.app.detail(download_url)
        urllib.request.urlretrieve(download_url, bin_file)
        p = Path(bin_file).stat()
        self.app.detail("{:,d} bytes downloaded".format(p.st_size))


class CloudGwFetcher(UrlFetcher):
    def __fetch_impl__(self, bin_info, bin_file):
        if "info_url" not in bin_info:
            raise Exception("Missing info_url for bin")
        info_url = bin_info["info_url"]
        r = requests.get(info_url)
        o = r.json()
        download_url = o["url"]
        bin_info["url"] = download_url
        return super().__fetch_impl__(bin_info, bin_file)
