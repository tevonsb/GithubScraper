"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['GHSThreaded.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True, 'iconfile':'Icon.icns'}

setup(
    app=APP,
    name = 'Github Scraper',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
