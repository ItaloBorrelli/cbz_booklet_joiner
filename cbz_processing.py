import shutil
import zipfile
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image
import re

def create_extracted_folder(base_path: str) -> Path:
    """Creates a folder inside the given base path."""
    folder_path = Path(base_path) / f"extracted"
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

def unzip_cbz(file_name: Path, extract_to: Path):
    """Extracts a CBZ file to the specified directory, renaming files with the CBZ name as a prefix."""
    cbz_name = file_name.stem  # Get filename without extension
    
    if file_name.exists():
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            for file in zip_ref.namelist():
                file_path = Path(file)
                # Ensure the file is not a directory
                if not file_path.name:
                    continue
                
                extracted_file_name = extract_to / f"{cbz_name}_{file_path.name}"
                
                with zip_ref.open(file) as source, open(extracted_file_name, "wb") as target:
                    shutil.copyfileobj(source, target)

def split_double_page_images(output_dir: Path):
    """Finds images with a hyphen (e.g., 1089_04-05.jpg) and splits them vertically."""
    for img_file in output_dir.glob("*.jpg"):
        match = re.search(r"_(\d+)-(\d+)\.jpg$", img_file.name)  # Match page numbers with hyphens
        if match:
            page1, page2 = match.groups()
            base_name = img_file.stem.split("_")[0]  # Extract base CBZ name
            with Image.open(img_file) as img:
                width, height = img.size
                mid = width // 2  # Find the middle of the image

                # Split the image into two halves
                right_half = img.crop((mid, 0, width, height))  # Right half (first page)
                left_half = img.crop((0, 0, mid, height))  # Left half (second page)

                # Save right page first, then left
                right_half.save(output_dir / f"{base_name}_{page1}.jpg")
                left_half.save(output_dir / f"{base_name}_{page2}.jpg")

            # Remove original double-page file
            img_file.unlink()
            print(f"Split {img_file.name} -> {base_name}_{page1}.jpg, {base_name}_{page2}.jpg")

def load_no_swap_list(no_swap_string: str, all_cbz_names: set) -> set:
    """Parses a comma-separated string of CBZ names that should NOT swap _01 with _00.
    
    Special cases:
    - 'none': No CBZs are excluded (empty set, meaning all will be swapped).
    - 'all': All CBZs are excluded from swapping (full set, meaning none will be swapped).
    """
    if not no_swap_string or no_swap_string.lower() == "none":
        return set()  # Swap everything (empty set means no exclusions)
    if no_swap_string.lower() == "all":
        return all_cbz_names  # Swap nothing (full set means exclude all)

    return {name.strip() for name in no_swap_string.split(",") if name.strip()}

def swap_01_with_00(output_dir: Path, no_swap_list: set):
    """Swaps _01.jpg with _00.jpg or _001.jpg with _000.jpg for CBZs NOT in the no_swap_list."""
    for img_file in output_dir.glob("*.jpg"):
        match = re.search(r"^(.*)_(0+1)\.jpg$", img_file.name)  # Matches _01, _001, _0001, etc.
        if match:
            cbz_name, page_01 = match.groups()
            page_00 = page_01.replace("1", "0", 1)  # Replace the last '1' with '0' (e.g., 01 → 00, 001 → 000)

            if cbz_name not in no_swap_list:  # Only swap if NOT in the list
                img_00 = output_dir / f"{cbz_name}_{page_00}.jpg"
                img_01 = output_dir / f"{cbz_name}_{page_01}.jpg"

                if img_00.exists():
                    temp_path = output_dir / f"{cbz_name}_temp.jpg"
                    img_01.rename(temp_path)
                    img_00.rename(img_01)
                    temp_path.rename(img_00)
                    print(f"Swapped {cbz_name}_{page_01}.jpg with {cbz_name}_{page_00}.jpg")

def scale_images(output_dir: Path, max_width: int, max_height: int, convert_format: str = "jpg"):
    """
    Scales images to fit within the given width and height while maintaining aspect ratio.
    Optionally converts images to PNG or WebP before resizing.
    
    Args:
        output_dir (Path): Directory containing images.
        max_width (int): Maximum width allowed.
        max_height (int): Maximum height allowed.
        convert_format (str): "jpg" (default), "png" (lossless but large), or "webp" (better compression).
    """
    for img_file in output_dir.glob("*.jpg"):
        with Image.open(img_file) as img:
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height

            # Calculate the two possible scaled sizes
            width_scaled_height = int(max_width / aspect_ratio)
            height_scaled_width = int(max_height * aspect_ratio)

            # Choose the best fit within the limits
            if width_scaled_height <= max_height:
                new_size = (max_width, width_scaled_height)
            else:
                new_size = (height_scaled_width, max_height)

            img_resized = img.resize(new_size, Image.LANCZOS)

            # Determine the save format
            save_format = convert_format.lower()
            if save_format == "png":
                new_file = img_file.with_suffix(".png")
                img_resized.save(new_file, format="PNG")
            elif save_format == "webp":
                new_file = img_file.with_suffix(".webp")
                img_resized.save(new_file, format="WEBP", quality=95)
            else:  # Default: JPG
                new_file = img_file
                img_resized.save(new_file, format="JPEG", quality=95, progressive=True)

            print(f"Resized {img_file.name} -> {new_size}, saved as {new_file.suffix.upper()}")

            # Delete original JPG if converted
            if convert_format in {"png", "webp"}:
                img_file.unlink()


def main():
    parser = argparse.ArgumentParser(description="Extract and process CBZ files into a structured directory.")
    parser.add_argument("--page-height", type=int, default=1500, help="Height of output page images (default: 1500 pixels height)")
    parser.add_argument("--page-width", type=int, default=1000, help="Width of output page images (default: 1000 pixels height)")
    parser.add_argument("--input-dir", type=str, required=True, help="Directory containing CBZ files")
    parser.add_argument(
        "--no-swap-01", type=str,
        help="Comma-separated CBZ names to exclude from swapping, or use 'all' to disable swapping and 'none' to swap all."
    )
    parser.add_argument("--convert-format", type=str, choices=["jpg", "png", "webp"], default="jpg", help="Convert images to jpg (default), png (lossless), or webp (smaller, better compression)")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: Input directory '{args.input_dir}' does not exist or is not a directory.")
        return
    
    output_dir = create_extracted_folder(input_path)

    for cbz_file in input_path.glob("*.cbz"):
        unzip_cbz(cbz_file, output_dir)
        print(f"Extracted: {cbz_file.name} -> {output_dir}")

    split_double_page_images(output_dir)

    # Get all CBZ base names in the input directory
    all_cbz_names = {cbz_file.stem for cbz_file in input_path.glob("*.cbz")}

    # Load no-swap list from a string, considering 'none' and 'all'
    no_swap_01_list = load_no_swap_list(args.no_swap_01, all_cbz_names) if args.no_swap_01 else set()

    swap_01_with_00(output_dir, no_swap_01_list)

    scale_images(output_dir, args.page_width, args.page_height, args.convert_format)

if __name__ == "__main__":
    main()
