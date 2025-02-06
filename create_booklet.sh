#!/bin/bash

# Check if a folder argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/folder"
    exit 1
fi

# Set target directory
TARGET_DIR="$1"

# Ensure the provided path is a valid directory
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

# Create an output directory for booklet spreads
OUTPUT_DIR="${TARGET_DIR}/booklet_spreads"
mkdir -p "$OUTPUT_DIR"

# Get a sorted list of image files
IMAGES=($(ls "$TARGET_DIR"/*.jpg | sort -V))

# Process pages in groups of 24
spread_number=1
total_pages=${#IMAGES[@]}

for ((i = 0; i < total_pages; i += 24)); do
    # Extract a batch of 24 pages
    PAGES=("${IMAGES[@]:i:24}")
    num_pages=${#PAGES[@]}

    # Determine pairs: First with Last, Second with Second-Last, etc.
    for ((j = 0; j < num_pages / 2; j++)); do
        LEFT_PAGE="${PAGES[j]}"
        RIGHT_PAGE="${PAGES[num_pages - j - 1]}"

        # Get filenames without path
        LEFT_NAME=$(basename "$LEFT_PAGE")
        RIGHT_NAME=$(basename "$RIGHT_PAGE")

        # Output file
        OUTPUT_FILE="${OUTPUT_DIR}/spread_$(printf "%02d" $spread_number).jpg"

        # Combine the two images side by side into 2000x1500 px
        convert -size 2000x1500 xc:white \
            "$LEFT_PAGE" -resize 1000x1500\! -gravity West -composite \
            "$RIGHT_PAGE" -resize 1000x1500\! -gravity East -composite \
            "$OUTPUT_FILE"

        echo "Created spread: $OUTPUT_FILE ($LEFT_NAME + $RIGHT_NAME)"

        ((spread_number++))
    done
done

echo "✅ All booklet spreads created in: $OUTPUT_DIR"

