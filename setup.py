from setuptools import setup, find_packages

setup(name="todo", packages=find_packages(), extras_require={"tests": ["pytest"]})
