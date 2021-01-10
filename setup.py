import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="portable-spreadsheet",
    version="2.0.2",
    author="David Salac",
    author_email="info@davidsalac.eu",
    description="A simple spreadsheet that keeps tracks of each operation of each cell in defined languages. Logic allows exporting sheets to Excel files (and see how each cell is computed), to the JSON strings with a description of computation of each cell (e. g. in the native language). Other formats, like HTML, CSV and Markdown (MD), are also implemented (user can define own format). It also allows reconstructing behaviours in native Python with NumPy.",  # noqa
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/david-salac/Portable-spreadsheet-generator",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'numpy-financial', 'XlsxWriter'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
