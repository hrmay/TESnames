import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="tesnames",
    version="1.0.0",
    author="Hannah May",
    author_email="hrmay@protonmail.com",
    description="A simple name generator that generates names using a Markov chain.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hrmay/TESnames",
    install_requires=requirements,
    packages=setuptools.find_packages(),
	package_data={'': ['names/**/*', 'names/**/*', 'names/**/**/*']},
    include_package_data=True,
    classifiers=[
    ],
    python_requires='>=3.6',
)
