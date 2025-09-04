import os
import json
import unittest

from housing_passports.db_package import (
    _get_session,
    add_buildings,
    add_images,
    distill_building_metadata,
    export_detection_geometry,
    export_to_db,
    link_db_detections,
)


class DBExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_url = "postgresql://postgres:1234@hpdb:5432/db_passport"
        cls.session = _get_session(cls.db_url)
        input_dir = "files_for_db"
        cls.geomfile_fpath = input_dir + "/dominica_buildings/01_osm_buildings.geojson"
        cls.trajectory_fpath = input_dir + "/trajectory_rc.csv"
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


class LinkDBDetectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_url = "postgresql://postgres:1234@hpdb:5432/db_passport"
        cls.neighborhood = "my_hood"

    def test_link_db_detections(self):
        link_db_detections(self.db_url, self.neighborhood)


class DistillMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_url = "postgresql://postgres:1234@hpdb:5432/db_passport"
        input_dir = "files_for_db"
        cls.fpath_parts = input_dir + "/parts_key.json"
        cls.fpath_property_groups = input_dir + "/properties_key.json"
        cls.neighborhood = "my_hood"

    def test_distill_building_metadata(self):
        distill_building_metadata(
            self.db_url,
            self.fpath_parts,
            self.fpath_property_groups,
            self.neighborhood,
        )


class ExportDetectionGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_url = "postgresql://postgres:1234@hpdb:5432/db_passport"
        input_dir = "files_for_db"
        cls.fpath_parts = input_dir + "/parts_key.json"
        cls.fpath_property_groups = input_dir + "/properties_key.json"
        cls.neighborhood = "my_hood"
        cls.linked_dets_only = True
        out_dir = "triangulation_results"
        cls.save_dir = f"{out_dir}/detections_ray/"
        os.makedirs(cls.save_dir, exist_ok=True)
        cls.save_fpath = f"{cls.save_dir}/{cls.neighborhood}_lines_ok.geojson"

        cls.neighborhood = "my_hood"
        # I think should be all the class names
        cls.det_classes = [
            "unsecured",
            "good",
            "secured",
            "fair",
            "plaster",
            "residential",
            "incomplete",
            "complete",
        ]

    def test_export_detection_geometry(self):
        export_detection_geometry(
            self.db_url,
            self.save_fpath,
            self.neighborhood,
            self.det_classes,
            self.linked_dets_only,
        )
