import json
import unittest

from housing_passports.db_package import (
    _get_session,
    add_buildings,
    add_images,
    export_to_db,
)


class DBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_url = "postgresql://postgres:1234@hpdb:5432/db_passport"
        cls.session = _get_session(cls.db_url)
        input_dir = "files_for_db"
        cls.geomfile_fpath = input_dir + "/dominica_buildings/01_osm_buildings.geojson"
        cls.trajectory_fpath = input_dir + "/trajectory.csv"
        cls.parts_inference_fpath = input_dir + "/parts_inference_file.json"
        cls.props_inference_fpath = input_dir + "/props_inference_file.json"
        cls.parts_map_fpath = input_dir + "/parts_map_file.pbtxt"
        cls.props_map_fpath = input_dir + "/props_map_file.pbtxt"

    def test_add_buildings(self):
        add_buildings(self.geomfile_fpath, self.session)
        self.session.commit()

    def test_add_images(self):
        add_images(self.trajectory_fpath, self.session)
        self.session.commit()

    def test_export_to_db(self):
        export_to_db(
            self.db_url,
            self.trajectory_fpath,
            self.geomfile_fpath,
            self.parts_inference_fpath,
            self.props_inference_fpath,
            self.parts_map_fpath,
            self.props_map_fpath,
        )


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_url = "postgresql://postgres:1234@hpdb:5432/db_passport"
        input_dir = "files_for_db"
        cls.geomfile_fpath = input_dir + "/dominica_buildings/01_osm_buildings.geojson"
        cls.trajectory_fpath = input_dir + "/trajectory.csv"
        cls.parts_inference_fpath = input_dir + "/parts_inference_file.json"
        cls.props_inference_fpath = input_dir + "/props_inference_file.json"
        cls.parts_map_fpath = input_dir + "/parts_map_file.pbtxt"
        cls.props_map_fpath = input_dir + "/props_map_file.pbtxt"

    def test_load_parts_inference_fpath(self):
        with open(self.parts_inference_fpath, "r") as json_file:
            data = json.load(json_file)
