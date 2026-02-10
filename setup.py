"""Setup script for epicsdev_tektronix package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

#with open("requirements.txt", "r", encoding="utf-8") as fh:
#    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="epicsdev_tektronix",
    version="1.0.2",
    author="Andrey Sukhanov",
    author_email="",
    description="EPICS PVAccess server for Tektronix MSO oscilloscopes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ASukhanov/epicsdev_tektronix",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    python_requires=">=3.7",
    #install_requires=requirements,
    keywords="epics oscilloscope tektronix mso pvaccess scpi visa",
    project_urls={
        "Bug Reports": "https://github.com/ASukhanov/epicsdev_tektronix/issues",
        "Source": "https://github.com/ASukhanov/epicsdev_tektronix",
        "Documentation": "https://github.com/ASukhanov/epicsdev_tektronix/blob/main/README.md",
    },
)
