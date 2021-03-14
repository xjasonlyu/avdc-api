import setuptools

with open('README.md') as file_readme:
    readme = file_readme.read()

with open('requirements.txt') as file_requirements:
    requirements = file_requirements.read().splitlines()

setuptools.setup(
    name="AVDC",
    version="0.1.0",
    license="GPL-3.0",
    author="xjasonlyu",
    description="AV_Data_Capture",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/xjasonlyu/AVDC",
    packages=setuptools.find_packages(),
    zip_safe=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GPL-3.0 License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Communications :: Chat",
        "Topic :: Printing",
        "Topic :: Text Processing :: General"
    ]
)
