import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="portable-spreadsheet-david-salac",
    version="0.0.1",
    author="David Salac",
    author_email="info@davidsalac.eu",
    description="Simple spreadsheet that keeps tracks of each operation "
                "in defined languages.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/david-salac/Portable-spreadsheet-generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
