import os
from setuptools import setup, find_packages

pkg_name = "olympus_wifi"

# Get version
exec(open(os.path.join(pkg_name, "version.py")).read())

setup(
    name=pkg_name,
    version=__version__,
    url=f"https://github.com/korjaa/{pkg_name}",
    description="Library to control Olympus cameras through WiFi.",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            f'{pkg_name}={pkg_name.replace("-", "_")}.cli:main'
        ]
    },
    python_requires='~= 3.7',
    install_requires=[
        "requests ~= 2.31",
        "dbus-python ~= 1.3"
    ],
)
