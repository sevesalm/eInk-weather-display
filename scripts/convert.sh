#!/bin/bash

# Converts all SVG icons to PNG images using rsvg-convert. 
# You might need to install it before using the script.

rm eInk-weather-display/png_icons/*
for f in svg_icons/*.svg
do
  echo Converting $f
  rsvg-convert -w 400 $f > eInk-weather-display/png_icons/$(basename $f .svg).png
done
