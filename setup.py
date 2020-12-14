from setuptools import setup, find_packages


setup(
    name="SVBot",
    version="0.4.1",

    description="A modular and extensible Discord bot.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    author="Abhishek Kumar",
    author_email="abhi.kr.2100@gmail.com",

    scripts=['bot.py'],
    packages=find_packages()
)