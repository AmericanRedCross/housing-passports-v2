# Usage


Define your mapillary access token
https://www.mapillary.com/dashboard/developers
```
export MAPILLARY_ACCESS_TOKEN="MLY|..."
```

Build the necessary image for preprocessing
```
cd spherical2images
git submodule update --init --recursive
docker compose build
cd ..
```

Download the data from mapillary and preprocess it
```
bash pre_processing/pre_processing.sh
```

Start and run the object detection inference and clipping notebook
`redcross_detectron2_workflow_iterate.ipynb`
```
cd nbs
jupyter notebook --ip $(hostname -I | awk '{print $1}')
```

This is currently set to process a single mapillary sequence (currently
sequence Qycm8N0gHbjkBZCtdxMoY3) for a specific side (currently the right
side).

NOTE: currently the predictions are hard-coded dummy predictions that are just
used to test the subsequent triangulation steps.

TODO: use predictions from the red cross models.

This outputs a file called `predictions_rc_right.csv` to the `output`
directory found in the same directory as the notebook file.


# Prepare data for triangulation


Go to the `prepare_data_for_triangulation` directory.
```
cd ~/housing-passports-v2/triangulation/prepare_data_for_triangulation
```

Copy the predictions file created above to this directory
```
cp -r ~/housing-passports-v2/nbs/output/predictions_rc_right.csv .
```

Launch the development container
```
docker compose run --rm --name prepare_data_for_triangulation-hpdev-run-1 hpdev bash
```

In a new terminal window in the same diretory, run the command to combine the
relevant data for triangulation
```
docker exec -it prepare_data_for_triangulation-hpdev-run-1 python3 -m unittest tests.tests.AttachDataTests.test_combine_resources
```

# Run the triangulation

Copy over the prepared data to the triangulation directory
```
cp -r ~/housing-passports-v2/triangulation/prepare_data_for_triangulation/data/files_for_db ~/housing-passports-v2/triangulation
```

NOTE: the proper geojson file that has the building footprints also needs to
be included for triangulation. This is currently already included here
`~/housing-passports-v2/triangulation/files_for_db/dominica_buildings/01_osm_buildings.geojson`
so nothing else needs to be done. However, this will need to change for
different areas of interest.

Build the image
```
cd ~/housing-passports-v2/triangulation
docker-compose build
```

(Re)Start the fresh database (no data)
```
cd ~/housing-passports-v2/triangulation
docker-compose stop hpdb
docker-compose rm hpdb
sudo rm -r postgres-data/
docker-compose up -d hpdb
```

Launch the development container to interact with the database
```
docker-compose run --rm --name triangulation-hpdev-run-1 hpdev bash
```

In a new terminal window in the same diretory, export the data to the database
```
docker exec -it triangulation-hpdev-run-1 python3 -m unittest tests.test_db_package.DBExportTests.test_export_to_db
```

Link the detections in the database
```
docker exec -it triangulation-hpdev-run-1 python3 -m unittest tests.test_db_package.LinkDBDetectionsTests.test_link_db_detections
```

Distill the metadata
```
vim tests/test_db_package.py
docker exec -it triangulation-hpdev-run-1 python3 -m unittest tests.test_db_package.DistillMetadataTests.test_distill_building_metadata
```

Export the detection geometry
```
docker exec -it triangulation-hpdev-run-1 python3 -m unittest tests.test_db_package.ExportDetectionGeometryTests.test_export_detection_geometry
```

View the file
`~/housing-passports-v2/triangulation/triangulation_results/detections_ray/my_hood_lines_ok.geojson`
with QGIS or a browser alternative (e.g. https://geojson.io/).
