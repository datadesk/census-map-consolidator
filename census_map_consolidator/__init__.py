#! /usr/bin/env python
"""
Where it happens.
"""
import collections
import json
import logging
import pathlib
import zipfile
from urllib.request import urlretrieve

import geopandas as gpd

logger = logging.getLogger(__name__)


class BlockConsolidator:
    """
    Consolidates the provided Census blocks into a new shape.
    """

    THIS_DIR = pathlib.Path(__file__).parent

    def __init__(self, *block_list, data_dir=None):
        self.block_list = block_list
        self.county_list = self.resolve_counties()
        self.zip_list = self.resolve_zipfiles()
        self.shp_list = self.resolve_shapefiles()
        if data_dir:
            self.data_dir = pathlib.Path(str(data_dir))
        else:
            self.data_dir = self.THIS_DIR.joinpath("data")
            if not self.data_dir.exists():
                self.data_dir.mkdir()

    def write(self, path):
        """
        Writes the consolidated SHP file to the provided path.
        """
        if ".geojson" in str(path):
            geojson = json.loads(self.consolidated_shp.to_json())
            with open(path, "w") as f:
                f.write(json.dumps(geojson, indent=4))
        else:
            self.consolidated_shp.to_file(path)

    def consolidate(self):
        """
        Merge the block list into a new shape.
        """
        # Ensure that all the ZIP files are downloaded
        [self.download_zipfile(z) for z in self.zip_list]

        # Ensure that all the ZIP files are unzipped.
        [self.unzip(z) for z in self.zip_list]

        # Load all of the SHP files into a GeoDataFrame
        shp_path_list = [self.data_dir.joinpath(shp) for shp in self.shp_list]
        gdf_list = []
        for path in shp_path_list:
            logger.debug(f"Reading in {path}")
            gdf_list.append(gpd.read_file(path))
        gdf = gpd.pd.concat(gdf_list)
        logger.debug(f"Loaded DataFrame with {len(gdf)} blocks")

        # Filter them down to only those in the block list
        logger.debug(
            f"Filtering down to the {len(self.block_list)} GEOIDs in the provided block list"
        )
        gdf.loc[gdf.GEOID10.isin(self.block_list), "to_dissolve"] = 1
        filtered_gdf = gdf[gdf.to_dissolve == 1]
        logger.debug(f"{len(filtered_gdf)} blocks found")

        # Dissolve the shapes together
        logger.debug("Dissolving the geometries")
        dissolved_shape = filtered_gdf.dissolve(by="to_dissolve")

        # Trime and project
        consolidated_shp = dissolved_shape[["geometry"]].to_crs(epsg=4326)

        # Hook it to the instance
        self.consolidated_shp = consolidated_shp

        # And pass it back for anybody running this inside a bigger script
        return consolidated_shp

    def resolve_counties(self):
        """
        Returns a list of all the counties in the block list.
        """
        geoids = [self.parse_geoid(b) for b in self.block_list]
        counties = [f"{g['state']}{g['county']}" for g in geoids]
        return list(set(counties))

    def resolve_zipfiles(self):
        """
        Returns a list of the ZIP file that correspond with the county list.
        """
        return [f"tl_2010_{county}_tabblock10.zip" for county in self.county_list]

    def resolve_shapefiles(self):
        """
        Returns a list of SHP file that correspond with the county list.
        """
        return [f"tl_2010_{county}_tabblock10.shp" for county in self.county_list]

    def parse_geoid(self, geoid):
        """
        Breaks up the provided Census GEOID into its component parts.

        Returns a dictionary with each part labeled.

        Documentation: https://www.census.gov/geo/reference/geoidentifiers.html
        """
        return collections.OrderedDict(
            (
                ("state", geoid[:2]),
                ("county", geoid[2:5]),
                ("tract", geoid[5:11]),
                ("block", geoid[11:]),
            )
        )

    def download_zipfile(self, zip_name):
        """
        Downloads the TIGER SHP file of Census block for the provided state and county.

        Returns the path to the ZIP file.
        """
        # Check if the zip file already exists
        zip_path = self.data_dir.joinpath(zip_name)
        if zip_path.exists():
            logger.debug(f"ZIP file already exists at {zip_path}")
            return zip_path

        # If it doesn't, download it from the Census FTP
        url = f"https://www2.census.gov/geo/tiger/TIGER2010/TABBLOCK/2010/{zip_name}"
        logger.debug(f"Downloading {url} to {zip_path}")
        urlretrieve(url, zip_path)

        # Return the path
        return zip_path

    def unzip(self, zip_name):
        """
        Unzip the provided ZIP file.
        """
        shp_path = pathlib.Path(zip_name.replace(".zip", ".shp"))
        if shp_path.exists():
            logger.debug(f"SHP already unzipped at {shp_path}")
            return shp_path

        zip_path = self.data_dir.joinpath(zip_name)
        logger.debug(f"Unzipping {zip_path} to {self.data_dir}")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(self.data_dir)
        return shp_path
