import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    'pandas',
    'numpy',
    'dateutils',
    'matplotlib',
    'pip',
    'convertdate',
    'holidays'
]

setuptools.setup(
    name="ramp-mobility",
    version="1.0.0",
    author="Francesco Lombardi, Francesco Sanvito, Sylvain Quoilin, Katija Pavicevic, Emanuela Colombo",
    author_email="f.lombardi@tudelft.nl",
    description="a RAMP application for generating bottom-up stochastic electric vehicles load profiles",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url="https://github.com/RAMP-project/RAMP-mobility",
    project_urls={},
    classifiers=[],
    packages=setuptools.find_packages(),
    python_requires = ">=3.7",
    include_package_data=True,
    package_data={'': ['database/*.csv', 'database/residual_load/*.csv']}
)