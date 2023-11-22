"""
Script for merge original data and cvat output
"""
from utils.index import (
    read_geojson,
    write_geojson,
    read_csv,
    write_dictlist2csv,
    write_json,
    write_pbtxt_content,
)
from tqdm import tqdm
import fire
import geopandas as gpd
from copy import deepcopy
from shapely import wkb

BUILDING_PROPERTIES = [
    "box_attr_building_condition",
    "box_attr_building_material",
    "box_attr_building_use",
    "box_attr_building_security",
    "box_attr_building_completeness",
]

BUILDING_PROPS = {
    "brick_or_cement-concrete_block": 1,
    "plaster": 2,
    "wood_polished": 3,
    "wood_crude-plank": 4,
    "adobe": 5,
    "corrugated_metal": 6,
    "stone_with_mud-ashlar_with_lime_or_cement": 7,
    "container-trailer": 8,
    "plant_material": 9,
    "mix-other-unclear": 10,
    "complete": 11,
    "incomplete": 12,
    "residential": 13,
    "mixed": 14,
    "commercial": 15,
    "critical_infrastructure": 16,
    "unsecured": 17,
    "secured": 18,
    "fair": 19,
    "poor": 20,
    "good": 21,
}

BUILDING_PARTS = {"window": 1, "door": 2, "garage": 3, "disaster_mitigation": 4}
IMAGE_SIDE = {
    "right": 1,
    "left": 2,
}


def combine_resources(
        annotation_properties_csv,
        annotation_parts_csv,
        original_geojson,
        gpkg_buildings_file,
        geojson_merge_output,
        shp_buildings_file,
        csv_output_trajectory,
        props_inference_file,
        props_map_file,
        parts_inference_file,
        parts_map_file,
):
    features = read_geojson(original_geojson)
    csv_data_props = read_csv(annotation_properties_csv)
    csv_data_parts = read_csv(annotation_parts_csv)

    list_data_annotation = [*csv_data_props, *csv_data_parts]
    df_polygons = gpd.read_file(gpkg_buildings_file)
    # group csv data
    csv_groups = {}
    for box in tqdm(list_data_annotation, desc="join data"):
        fake_key = f'{box["img_path"]}/{box["img_name"]}'
        if not csv_groups.get(fake_key):
            csv_groups[fake_key] = []
        csv_groups[fake_key].append(box)

    for feature in tqdm(features, desc="merge features"):
        props = feature["properties"]
        fake_key = "/".join(props.get("image_path", "").split("/")[-3:])
        props["box"] = csv_groups.get(fake_key, [])

    write_geojson(geojson_merge_output, features)
    # housing_passports formats
    trajectories_out = []
    building_props_out = []
    building_parts_out = []

    for feature in tqdm(features, desc="Hp  create format"):
        props = feature.get("properties", {})
        lat, lng = feature.get("geometry", {}).get("coordinates")
        path_seq = props.get("image_path", "").split("/")
        image_name = path_seq[-1]

        trajectory = {
            "heading[deg]": props.get("compass_angle"),
            "image_fname": image_name,
            "frame": image_name.split(".")[0],
            "latitude[deg]": lat,
            "longitude[deg]": lng,
            "cam": IMAGE_SIDE.get(path_seq[-2], 0),
            "neighborhood": "n1",
            "subfolder": "/".join(path_seq[-3:-1]),
        }
        box_props = {
            "detection_scores": [],
            "detection_classes": [],
            "detection_boxes": [],
            "image_fname": image_name,
            "subfolder": "/".join(["data", *path_seq[-3:-1]]),
            "cam": IMAGE_SIDE.get(path_seq[-2], 0),
            "frame": image_name.split(".")[0],
            "neighborhood": "n1",
        }
        box_building_props = deepcopy(box_props)
        box_building_parts = deepcopy(box_props)

        trajectories_out.append(trajectory)

        for box_meta in props.get("box", []):
            box = [
                float(box_meta.get("box_xtl", "")),
                float(box_meta.get("box_ytl", "")),
                float(box_meta.get("box_xbr", "")),
                float(box_meta.get("box_ybr", "")),
            ]

            box_label = box_meta.get("box_label")
            if not box_label:
                continue
            if box_label == "building_properties":
                for prop_key in BUILDING_PROPERTIES:
                    if box_meta.get(prop_key):
                        new_key = BUILDING_PROPS.get(box_meta.get(prop_key))
                        box_building_props["detection_boxes"].append(deepcopy(box))
                        box_building_props["detection_classes"].append(new_key)
                        box_building_props["detection_scores"].append(1)

            else:
                new_key = BUILDING_PARTS.get(box_label)
                box_building_parts["detection_boxes"].append(deepcopy(box))
                box_building_parts["detection_classes"].append(new_key)
                box_building_parts["detection_scores"].append(1)

        building_props_out.append(deepcopy(box_building_props))
        building_parts_out.append(deepcopy(box_building_parts))

    # write_json(BUILDING_PROPS, )
    # write files
    write_dictlist2csv(csv_output_trajectory, trajectories_out)
    # write props
    write_json(props_inference_file, building_props_out)
    write_json(parts_inference_file, building_parts_out)

    write_pbtxt_content(props_map_file, BUILDING_PROPS)
    write_pbtxt_content(parts_map_file, BUILDING_PARTS)

    # write shp
    df_polygons["neighborhood"] = "n1"
    df_polygons = df_polygons.to_crs(4326)
    df_polygons["geometry"] = df_polygons["geometry"].apply(
        lambda geom: geom
        if geom.is_empty
        else wkb.loads(wkb.dumps(geom, output_dimension=2))
    )

    df_polygons.to_file(shp_buildings_file, driver="ESRI Shapefile")


def main():
    fire.Fire(combine_resources)


if __name__ == "__main__":
    main()
