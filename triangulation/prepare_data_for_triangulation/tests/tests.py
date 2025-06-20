import unittest

from pipeline.attach_data import (
    add_geom,
    combine_resources,
    include_geom,
    read_geojson,
    rm_geom,
    add_image_path
)


class AttachDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_out = "data"
        data_prepared = f"{ data_out }/files_for_db"
        shp_out = f"{ data_prepared }/shp_building"

        cls.predictions_csv = f"{ data_out }/all_predictions_with_scores.csv"
        cls.predictions_csv = f"{ data_out }/predictions.csv"
        # cls.original_geojson = f"{ data_out }/01_osm_buildings.geojson"
        # cls.original_geojson = f"{ data_out }/mapillary_points_panoramic__pano__pano.geojson"
        cls.original_geojson = f"{ data_out }/mapillary_points_panoramic_process_new.geojson"
        cls.gpkg_buildings_file = f"{ data_out }/bldgs_buffer_DOM_3.gpkg"

        cls.prefix_path_images = f"{ data_out }/mapillary_images_new"
        cls.neighborhood = f"{ data_out }/01_bounds_polygon.geojson"
        cls.shp_buildings_file = f"{ shp_out }/shp_building.shp"
        cls.geojson_merge_output = f"{ data_prepared }/annotation_merge.geojson"
        cls.csv_output_trajectory = f"{ data_prepared }/trajectory_rc.csv"
        cls.props_inference_file = f"{ data_prepared }/props_inference_file.json"
        cls.props_map_file = f"{ data_prepared }/props_map_file.pbtxt"
        cls.parts_inference_file = f"{ data_prepared }/parts_inference_file.json"
        cls.parts_map_file = f"{ data_prepared }/parts_map_file.pbtxt"
        cls.props_keys_file = f"{ data_prepared }/properties_key.json"
        cls.part_keys_file = f"{ data_prepared }/parts_key.json"

    def test_see_features(self):
        features_areas_ = read_geojson(self.neighborhood)
        features_areas__ = add_geom(features_areas_)

        features_ = read_geojson(self.original_geojson)
        features__ = add_geom(features_)  # seems like Dan already did this step

        features_all = include_geom(features__, features_areas__)
        features = rm_geom(features_all)

        add_image_path(features)
        for feature in features:
            self.assertIn("image_path", feature["properties"])


    def test_combine_resources(self):
        combine_resources(
            self.predictions_csv,
            self.original_geojson,
            self.gpkg_buildings_file,
            self.prefix_path_images,
            self.neighborhood,
            self.shp_buildings_file,
            self.geojson_merge_output,
            self.csv_output_trajectory,
            self.props_inference_file,
            self.props_map_file,
            self.parts_inference_file,
            self.parts_map_file,
            self.props_keys_file,
            self.part_keys_file,
        )
