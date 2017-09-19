from setuptools import setup

setup(
    name='mongo_stats',
    version='0.1',
    py_modules=['mongo_stats'],
    install_requires=[
        'Click',
        'pymongo'
    ],
    entry_points={
        "console_scripts": [
            "mongo_stats=mongo_stats.stats:start"
        ]
    },
)
