'''
The setup.py file is an essential part of packaging and 
distributing Python projects. It is used by setuptools 
(or distutils in older Python versions) to define the configuration 
of your project, such as its metadata, dependencies, and more
'''

from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    requirements: List[str] = []
    try:
        with open("requirements.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement!= '-e .':
                    requirements.append(requirement)
            
    except FileNotFoundError:
        print("requirements.txt file not found")
    
    return requirements

setup(
    name="NetworkSecurity",
    version="0.1.0",
    author="Muhammad Imran Saeed",
    author_email="iamimransaeed1996@gmail.com",
    description="A package for network security tools and utilities",
    packages=find_packages(),
    install_requires=get_requirements()
)
