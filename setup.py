from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in custom_erpnext/__init__.py
from custom_erpnext import __version__ as version

setup(
	name="custom_erpnext",
	version=version,
	description="Customized ERPNext",
	author="Lithe-Tech Limited",
	author_email="rafeed.cse@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
