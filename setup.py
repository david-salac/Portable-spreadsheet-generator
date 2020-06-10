import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="portable-spreadsheet",
    version="0.1.12",
    author="David Salac",
    author_email="info@davidsalac.eu",
    description="Simple spreadsheet that keeps tracks of each operation in "
                "defined programming languages. Logic allows export sheets to "
                "Excel files (and see how each cell is computed), to the "
                "JSON strings with description of computation e. g. in "
                "native language. Other formats like HTML, CSV and "
                "Markdown (MD) are also supported. It also allows to "
                "reconstruct behaviours in native Python with NumPy.",
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
