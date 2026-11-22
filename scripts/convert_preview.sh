#!/bin/bash

set -euxo pipefail

# Converts all SVG icons to smaller PNG images using rsvg-convert. 
# You might need to install it before using the script.

mkdir -p eInk-weather-display/svg_icons/preview
rm eInk-weather-display/svg_icons/preview/*
for f in eInk-weather-display/svg_icons/*.svg
do
  echo Converting $f
  rsvg-convert -b white -h 100 $f > eInk-weather-display/svg_icons/preview/$(basename $f .svg).png
done
