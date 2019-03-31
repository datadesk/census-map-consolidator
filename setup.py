from setuptools import setup


setup(
    name='census-map-consolidator',
    version='0.0.4',
    description="Combine Census maps into new shapes",
    author='Ben Welsh',
    author_email='ben.welsh@gmail.com',
    url='http://www.github.com/datadesk/census-map-consolidator',
    license="MIT",
    packages=("census_map_consolidator",),
    install_requires=(
        "geopandas"
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
)
