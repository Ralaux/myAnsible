from setuptools import setup

setup(
    name='mla',
    version='1.0',
    packages=['mla'],
    entry_points={
        'console_scripts': [
            'mla = mla.main:main',
        ],
    },
    scripts=[
            'mla/my_parser.py',
            'mla/SSH_handler.py',
            'mla/todo_handler.py',
           ]
)