#!/bin/bash

# extract images from cbz
mkdir -p extracted
for file in {1089..1100}.cbz; do unzip -j "$file" -d extracted/"${file%.cbz}"; done

cd extracted || exit
for folder in {1089..1100}; do
  for img in "$folder"/*; do
    filename=$(basename "$img")
    mv "$img" "${folder}_$filename"
  done
done

for img in *-*.jpg; do
  if [ -f "$img" ]; then
    # Extract base name without extension
    base_name="${img%.*}"

    # Extract the prefix (e.g., 1089) and the page numbers (e.g., 04-05)
    prefix=$(echo "$base_name" | cut -d'_' -f1)
    page_numbers=$(echo "$base_name" | cut -d'_' -f2)

    # Extract first and second numbers from page numbers
    first_page=$(echo "$page_numbers" | cut -d'-' -f1)
    second_page=$(echo "$page_numbers" | cut -d'-' -f2)

    # Define output filenames with proper prefix
    right_output="${prefix}_${first_page}.jpg"
    left_output="${prefix}_${second_page}.jpg"

    # Split the image into left and right halves (keeping resolution & DPI)
    convert "$img" -gravity West -crop 50%x100%+0+0 "$left_output"
    convert "$img" -gravity East -crop 50%x100%+0+0 "$right_output"

    # Remove the original spread image
    rm "$img"
  fi
done

find . -type d -delete

mkdir -p scaled_images                      
for img in *.jpg; do
    convert "$img" -resize 1000x "scaled_images/$img"
done

cd scaled_images || exit
rm 1097_01.jpg 1098_001.jpg 1099_001.jpg 1100_001.jpg 1096_01.jpg 1095_01.jpg 1093_01.jpg 1092_01.jpg 1090_01.jpg 1089_01.jpg

./join_in_24s.sh

img2pdf joint_pages/*.jpg -o output.pdf
