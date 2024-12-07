from setuptools import setup, find_packages

setup(
    name="git-commit-generator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "gitpython>=3.1.0",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "pyyaml>=6.0.1",
        "pyinstaller>=5.0.0",  # 추가
    ],
    entry_points={
        "console_scripts": [
            "git-commit-generator=git_commit_generator.generator:main",
        ],
    },
    python_requires=">=3.8",
)