#!/bin/bash

# Check if a directory was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

input_dir="$1"

# Ensure the directory exists
if [ ! -d "$input_dir" ]; then
    echo "Error: Directory '$input_dir' does not exist."
    exit 1
fi

output_dir="$input_dir/spreads"
mkdir -p "$output_dir"

# Get list of images in strict numerical/alphabetical order
images=($(ls -1v "$input_dir"/*.jpg | sort -V))

# Process images, skipping ones already in spread format
i=0
while [ $i -lt ${#images[@]} ]; do
    img1="${images[$i]}"
    img_name1=$(basename "$img1")

    # Check if the filename is already a spread (contains "-")
    if [[ "$img_name1" == *-* ]]; then
        echo "Skipping already merged spread: $img_name1"
        cp "$img1" "$output_dir/$img_name1"
        ((i++))
        continue
    fi

    # Get the next image for pairing
    if [ $((i+1)) -lt ${#images[@]} ]; then
        img2="${images[$((i+1))]}"
        img_name2=$(basename "$img2")

        # If next image is already a spread, process current image alone
        if [[ "$img_name2" == *-* ]]; then
            echo "Keeping single page as is: $img_name1"
            cp "$img1" "$output_dir/$img_name1"
            ((i++))
            continue
        fi

        # Generate a new spread name
        num1=$(printf "%02d" $i)
        num2=$(printf "%02d" $((i+1)))
        spread_name="$output_dir/${num1}-${num2}.jpg"

        echo "Merging $img_name2 and $img_name1 -> $(basename "$spread_name")"
        convert +append "$img2" "$img1" "$spread_name"

        ((i+=2))
    else
        # Single page left alone if no pair is available
        echo "Keeping single page as is: $img_name1"
        cp "$img1" "$output_dir/$img_name1"
        ((i++))
    fi
done

# Convert to PDF
echo "Generating booklet PDF..."
img2pdf "$output_dir"/*.jpg -o "$input_dir/booklet.pdf"

echo "Done! Booklet saved as $input_dir/booklet.pdf"
