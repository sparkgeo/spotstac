__version__ = "0.1.0"
import json
import urllib.request
from urllib.parse import urlparse

import boto3
from pystac import STAC_IO

from . import spotstac as SpotSTAC


def read_remote_stacs(uri):
    """
    Reads STACs from a remote location. To be used to set STAC_IO
    Defaults to local storage.
    """
    parsed = urlparse(uri)
    if parsed.scheme == "s3":
        bucket = parsed.netloc
        key = parsed.path[1:]
        s3 = boto3.resource("s3")
        obj = s3.Object(bucket, key)
        return obj.get()["Body"].read().decode("utf-8")
    if parsed.scheme in ["http", "https"]:
        with urllib.request.urlopen(uri) as url:
            stac = url.read().decode()
            return stac
    else:
        return STAC_IO.default_read_text_method(uri)


def write_remote_stacs(uri, txt):
    """
    Writes STACs from a remote location. To be used to set STAC_IO
    Defaults to local storage.
    """
    parsed = urlparse(uri)

    def _s3_write(bucket, key):
        s3 = boto3.resource("s3")
        s3.Object(bucket, key).put(Body=txt, ContentType="application/json")

    if "s3" in parsed.netloc:
        _s3_write(parsed.netloc.split(".")[0], parsed.path[1:])
    elif parsed.scheme == "s3":
        _s3_write(parsed.netloc, parsed.path[1:])
    else:
        STAC_IO.default_write_text_method(uri, txt)


STAC_IO.read_text_method = read_remote_stacs
STAC_IO.write_text_method = write_remote_stacs
