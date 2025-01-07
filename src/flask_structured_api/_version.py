import os
import re


def get_version():
    """Read version from __version__.py"""
    version_file = os.path.join(os.path.dirname(__file__), "__version__.py")
    with open(version_file, "r") as f:
        content = f.read()
    version_match = re.search(r"VERSION\s*=\s*\((.*?)\)", content)
    if version_match:
        return ".".join(map(str.strip, version_match.group(1).split(",")))
    raise RuntimeError("Unable to find version string.")
