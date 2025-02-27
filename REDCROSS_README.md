# Usage


Define your mapillary access token
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
