import os
from pkg_resources import resource_filename


def data_file(path):
    pathparts = path.split("/")
    relpath = os.path.join("tests", "data", *pathparts)
    return resource_filename("yeat", relpath)
