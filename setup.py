from setuptools import setup, find_packages

setup(
    name="autodpd",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "packaging",
        "PyYAML",
    ],
    entry_points={
        "console_scripts": [
            "autodpd=autodpd.autodpd:main",
        ],
    },
    author="Dan Peng",
    author_email="dan.peng.1202@gmail.com",
    description="A tool to automatically analyze Python projects and generate dependency specifications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/greatdanpeng/autodepend",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
) 