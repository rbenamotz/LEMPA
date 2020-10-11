import shutil
from os import path
from pathlib import Path
from states.binfetchers import BinFetcher


class LocalFetcher(BinFetcher):
    def __fetch_impl__(self, bin_info, bin_file):
        if not path.exists(bin_file):
            raise Exception("missing bin: {}".format(bin_file))


class FSCopyFetcher(BinFetcher):
    def __fetch_impl__(self, bin_info, bin_file):
        if "src" not in bin_info:
            raise Exception("Missing src info")
        src = bin_info["src"]
        if not path.exists(src):
            raise Exception("missing bin: {}".format(src))
        self.app.detail("Copying {}".format(src))
        shutil.copy(src, bin_file)
        p = Path(bin_file).stat()
        self.app.detail("{} bytes copied".format(p.st_size))
