#!/usr/bin/env bash
outputDir=data
mkdir -p $outputDir
mkdir -p ${outputDir}/images_new

geokitdocker="docker run --rm -v ${PWD}:/mnt/data/  -e MAPILLARY_ACCESS_TOKEN=${MAPILLARY_ACCESS_TOKEN} -it developmentseed/geokit:python.develop mapillary"
spherical2imagesdocker="docker run -v $PWD:/mnt/ -e MAPILLARY_ACCESS_TOKEN=$MAPILLARY_ACCESS_TOKEN -it developmentseed/spherical2images:v1"


$geokitdocker get_mapillary_points \
   --input_aoi=112.748232,-7.304144,112.755635,-7.298302 \
   --organization_ids=1606999786835974 \
   --only_pano \
   --output_file_point=${outputDir}/mapillary_points_panoramic__pano.geojson \
   --output_file_sequence=${outputDir}/mapillary_sequences_panoramic__pano.geojson

   # --timestamp_from=1729641600000 \

$spherical2imagesdocker clip_mapillary_pano \
  --input_file_points=${outputDir}/mapillary_points_panoramic__pano__pano.geojson \
  --image_clip_size=1024 \
  --output_file_points=${outputDir}/mapillary_points_panoramic_process_new.geojson \
  --output_images_path=${outputDir}/images_new \
  --cube_sides=right,left
