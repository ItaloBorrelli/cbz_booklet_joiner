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

# Loop through all files matching the spread naming pattern in the given folder
for img in "$TARGET_DIR"/*-*.jpg; do
    if [ -f "$img" ]; then
        # Extract base name without extension
        base_name="${img%.*}"

        # Extract first and second numbers from filename
        first_page=$(basename "$base_name" | cut -d'-' -f1)
        second_page=$(basename "$base_name" | cut -d'-' -f2)

        # Define output filenames
        left_output="${TARGET_DIR}/${first_page}.jpg"
        right_output="${TARGET_DIR}/${second_page}.jpg"

        # Split the image into left and right halves (keeping resolution & DPI)
        convert "$img" -gravity West -crop 50%x100%+0+0 -resize 128x "$left_output"
        convert "$img" -gravity East -crop 50%x100%+0+0 -resize 128x "$right_output"

        # Remove the original spread image
        rm "$img"

        echo "Split and deleted: $(basename "$img") -> $(basename "$left_output"), $(basename "$right_output")"
    fi
done

# Get the folder name without path
FOLDER_NAME=$(basename "$TARGET_DIR")

# Ensure images are ordered correctly for booklet printing
SORTED_FILES=$(ls "$TARGET_DIR"/*.jpg | sort -V)

# Convert to PDF ensuring correct order
echo "Creating PDF: $TARGET_DIR/$FOLDER_NAME.pdf"
img2pdf --auto-orient $SORTED_FILES -o "$TARGET_DIR/$FOLDER_NAME.pdf"

echo "✅ Process complete: Created $FOLDER_NAME.pdf with correct resolution."

