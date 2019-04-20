import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyedid",
    version="0.0.1",
    author="Jonas Lieb",
    author_email="author@example.com",
    description="Python library to parse extended display identification data (EDID)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jojonas/pyedid",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
