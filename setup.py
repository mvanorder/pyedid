import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyedid",
    version="0.0.2",
    author="Jonas Lieb, Jonathan Dean",
    author_email="",
    description="Python library to parse extended display identification data (EDID)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ke4ukz/pyedid",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
