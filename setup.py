from setuptools import setup


setup(
    name='census-consolidator',
    version='0.0.1',
    description="Combine Census blocks into new shapes",
    author='Ben Welsh',
    author_email='ben.welsh@gmail.com',
    url='http://www.github.com/datadesk/census-consolidator',
    license="MIT",
    packages=("census_consolidator",),
    install_requires=(
        "fake-useragent",
        "geopandas",
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
)
