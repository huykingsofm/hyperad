import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    long_description += "\n"


with open("CHANGELOG.md", "r", encoding="utf-8") as fh:
    long_description += fh.read()


setuptools.setup(
    name="hyperad",
    version="0.0.1",
    author="huykingsofm",
    author_email="huykingsofm@gmail.com",
    description="A framework helps client applications communicate with"
        " web server via HTTP protocol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huykingsofm/hyperad",
    project_urls={
        "Bug Tracker": "https://github.com/huykingsofm/hyperad/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7.1",
    install_requires=[],
    setup_requires=["pytest-runner==4.4"],
    tests_require=["pytest==4.4.1"],
    test_suite="tests",
)