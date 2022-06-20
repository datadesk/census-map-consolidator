import pathlib
import unittest

import census_map_consolidator


class CensusConsolidateTest(unittest.TestCase):
    THIS_DIR = pathlib.Path(__file__).parent

    def setUp(self):
        self.data_dir = self.THIS_DIR.joinpath("test_data")

        self.dtla_block = "060371976001008"
        self.osceola_county_ia = "19143"
        self.la_county_ca = "06037"

        with open(self.data_dir.joinpath("dtla.csv")) as f:
            self.dtla_block_list = f.read().splitlines()

        self.consolidate_client = census_map_consolidator.BlockConsolidator(
            *self.dtla_block_list, data_dir=self.data_dir
        )

    def test_parse_geoid(self):
        geoid_dict = self.consolidate_client.parse_geoid(self.dtla_block)
        self.assertEqual(geoid_dict["state"], "06")
        self.assertEqual(geoid_dict["county"], "037")
        self.assertEqual(geoid_dict["tract"], "197600")
        self.assertEqual(geoid_dict["block"], "1008")

    def test_resolve_counties(self):
        counties = self.consolidate_client.resolve_counties()
        self.assertEqual(counties, [self.la_county_ca])

    def test_resolve_zipfiles(self):
        zips = self.consolidate_client.resolve_zipfiles()
        self.assertEqual(zips, ["tl_2010_06037_tabblock10.zip"])

    def test_resolve_shapefiles(self):
        shps = self.consolidate_client.resolve_shapefiles()
        self.assertEqual(shps, ["tl_2010_06037_tabblock10.shp"])

    def test_consolidate(self):
        self.consolidate_client.consolidate()
        self.consolidate_client.write(self.data_dir.joinpath("dtla.shp"))
        self.consolidate_client.write(self.data_dir.joinpath("dtla.geojson"))

    def test_download_shapefile(self):
        client = census_map_consolidator.BlockConsolidator(
            *["191434601001000", "191434601001001"]
        )
        client.consolidate()

    def tearDown(self):
        for p in pathlib.Path("census_map_consolidator/data").glob("*"):
            p.unlink()


if __name__ == "__main__":
    unittest.main()
