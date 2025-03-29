from setuptools import setup, find_packages

setup(
    name="fable-generator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.95.2",
        "uvicorn==0.22.0",
        "python-dotenv==1.0.0",
        "openai==0.27.0",
        "pytest==7.4.0",
        "httpx==0.24.0"
    ]
) 