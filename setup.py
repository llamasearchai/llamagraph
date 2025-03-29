from setuptools import setup, find_packages

setup(
    name="llamagraph",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "rich>=10.16.2",
        "click>=8.1.3",
        "textual>=0.24.1",
        "prompt_toolkit>=3.0.38",
        "mlx>=0.0.5",
        "tqdm>=4.65.0",
        "pyfiglet>=0.8.post1",
        "colorama>=0.4.6",
        "spacy>=3.5.3",
        "networkx>=3.1",
    ],
    entry_points={
        "console_scripts": [
            "llamagraph=llamagraph.cli:main",
        ],
    },
    python_requires=">=3.9",
    author="LlamaGraph Team",
    author_email="info@llamagraph.com",
    description="A llama-themed knowledge graph construction tool from text",
    keywords="knowledge graph, nlp, llama, mlx",
    url="https://github.com/llamagraph/llamagraph",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
) 