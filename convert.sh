#!/bin/bash

# Check if at least one argument (input file) is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <input-file> [output-file] [hex-color]"
    exit 1
fi

input="$1"
output="${2:-output.png}"   # Default output filename is "output.png"
bg_color="${3:-#FFFFFF}"    # Default background color is white (#FFFFFF)

# Temporary files
temp_resized="resized_temp.png"
temp_bordered="bordered_temp.png"

# Resize to 1460px tall while keeping aspect ratio
convert "$input" -resize x1460 "$temp_resized"

# Add 5px black border
convert "$temp_resized" -bordercolor black -border 5 "$temp_bordered"

# Add padding to reach 1000x1500 using the specified background color
convert "$temp_bordered" -gravity center -background "$bg_color" -extent 1000x1500 "$output"

# Cleanup intermediate files
rm -f "$temp_resized" "$temp_bordered"

echo "Done! Saved as $output with background color $bg_color"
