import sys
import pathlib
import zipfile
import logging
import collections
import urllib.request
import geopandas as gpd
from fake_useragent import UserAgent
logger = logging.getLogger(__name__)


class BlockConsolidator(object):
    """
    Consolidates the provided Census blocks into a new shape.
    """
    THIS_DIR = pathlib.Path(__file__).parent
    USER_AGENT = UserAgent()

    def __init__(self, *block_list, data_dir=None):
        self.block_list = block_list
        self.county_list = self.resolve_counties()
        self.zip_list = self.resolve_zipfiles()
        self.shp_list = self.resolve_shapefiles()
        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = self.THIS_DIR.joinpath("data")
            if not self.data_dir.exists():
                self.data_dir.mkdir()

    def write(self, path):
        """
        Writes the consolidated SHP file to the provided path.
        """
        if '.geojson' in str(path):
            self.consolidated_shp.to_file(path, driver="GeoJSON")
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
            print(f"Reading in {path}")
            gdf_list.append(gpd.read_file(path))
        gdf = gpd.pd.concat(gdf_list)
        print(f"Loaded DataFrame with {len(gdf)} blocks")

        # Filter them down to only those in the block list
        print(f"Filtering down to the {len(self.block_list)} GEOIDs in the provided block list")
        gdf.loc[gdf.GEOID10.isin(self.block_list), 'to_dissolve'] = 1
        filtered_gdf = gdf[gdf.to_dissolve == 1]
        print(f"{len(filtered_gdf)} blocks found")

        # Dissolve the shapes together
        print("Dissolving the geometries")
        self.consolidated_shp = filtered_gdf.dissolve(by='to_dissolve')

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
        return collections.OrderedDict((
            ("state", geoid[:2]),
            ("county", geoid[2:5]),
            ("tract", geoid[5:11]),
            ("block", geoid[11:]),
        ))

    def download_zipfile(self, zip_name):
        """
        Downloads the TIGER SHP file of Census block for the provided state and county.

        Returns the path to the ZIP file.
        """
        path = self.data_dir.joinpath(zip_name)

        if path.exists():
            print(f"ZIP file already exists at {path}")
            return path

        url = f"ftp://ftp2.census.gov/geo/tiger/TIGER2010/TABBLOCK/2010/{zip_name}"
        print(f"Downloading {url} to {path}")

        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': self.USER_AGENT.random
            }
        )
        u = urllib.request.urlopen(req)
        with open(path, 'wb') as f:
            file_size = int(u.headers["Content-Length"])
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                f.write(buffer)
        return path

    def unzip(self, zip_name):
        """
        Unzip the provided ZIP file.
        """
        shp_path = self.data_dir.joinpath(zip_name.replace(".zip", ".shp"))
        if shp_path.exists():
            print(f"SHP already unzipped at {shp_path}")
            return

        zip_path = self.data_dir.joinpath(zip_name)
        print(f"Unzipping {zip_name} to {self.data_dir}")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(self.data_dir)
