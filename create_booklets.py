from PIL import Image, ImageOps
import argparse
from pathlib import Path
from itertools import chain

def create_blank_page(width: int, height: int) -> Image.Image:
    """Creates a plain white image of the given dimensions."""
    return Image.new("RGB", (width, height), "white")

def collect_booklet_images(processed_dir: Path, start_pages_dir: Path, end_pages_dir: Path, target_width: int, target_height: int):
    """Collects all images into an array, adding blank pages where necessary."""
    booklet_images = []

    # Load and sort start pages
    start_pages = sorted(
        [img for img in start_pages_dir.glob("*") if img.suffix.lower() in {".jpg", ".png", ".webp"}]
    )
    
    # Add start pages
    booklet_images.extend(start_pages)

    # If the number of start pages is even, add one blank page
    if len(start_pages) % 2 == 0:
        blank_page_path = processed_dir / "blank_start.jpg"
        create_blank_page(target_width, target_height).save(blank_page_path)
        booklet_images.append(blank_page_path)

    # Load and sort processed pages
    processed_pages = sorted(
        [img for img in processed_dir.glob("*") if img.suffix.lower() in {".jpg", ".png", ".webp"}]
    )
    booklet_images.extend(processed_pages)

    # Load and sort end pages
    end_pages = sorted(
        [img for img in end_pages_dir.glob("*") if img.suffix.lower() in {".jpg", ".png", ".webp"}]
    )

    # Calculate total pages so far
    total_pages = len(booklet_images) + len(end_pages)
    
    # Add blank pages before the end pages to make total pages divisible by 4
    while total_pages % 4 != 0:
        blank_page_path = processed_dir / f"blank_padding_{total_pages}.jpg"
        create_blank_page(target_width, target_height).save(blank_page_path)
        booklet_images.append(blank_page_path)
        total_pages += 1

    # Add end pages
    booklet_images.extend(end_pages)

    print(f"Total pages in booklet: {len(booklet_images)} (should be multiple of 4)")
    
    return booklet_images

def scale_image(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Scales an image to match the target height."""
    # Scale height to match target height, keeping aspect ratio
    width, height = img.size
    scale_ratio = target_height / height
    new_width = int(width * scale_ratio)
    return img.resize((new_width, target_height), Image.LANCZOS)

def scale_and_save_images(input_dir: Path, output_dir: Path, target_width: int, target_height: int):
    """Scales images in `input_dir` to match target height and saves them in `output_dir`."""
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure output directory exists

    for img_file in sorted(input_dir.glob("*")):
        if img_file.suffix.lower() in {".jpg", ".png", ".webp"}:
            with Image.open(img_file) as img:
                scaled_img = scale_image(img, target_width, target_height)
                output_path = output_dir / img_file.name
                scaled_img.save(output_path)
                print(f"Scaled and saved: {output_path}")

def create_booklets(processed_dir: Path, start_pages_dir: Path, end_pages_dir: Path, target_width: int, target_height: int):
    """Processes booklets by scaling start and end pages before collecting all images."""
    if not processed_dir.exists() or not processed_dir.is_dir():
        print(f"Error: Processed directory '{processed_dir}' does not exist or is not a directory.")
        return
    if not start_pages_dir.exists() or not start_pages_dir.is_dir():
        print(f"Error: Start pages directory '{start_pages_dir}' does not exist or is not a directory.")
        return
    if not end_pages_dir.exists() or not end_pages_dir.is_dir():
        print(f"Error: End pages directory '{end_pages_dir}' does not exist or is not a directory.")
        return

    scaled_start_dir = processed_dir / "scaled_start"
    scaled_end_dir = processed_dir / "scaled_end"

    print("Scaling start pages...")
    scale_and_save_images(start_pages_dir, scaled_start_dir, target_width, target_height)

    print("Scaling end pages...")
    scale_and_save_images(end_pages_dir, scaled_end_dir, target_width, target_height)

    return collect_booklet_images(processed_dir, scaled_start_dir, scaled_end_dir, target_width, target_height)

def join_two_pages(left_img: Image.Image, right_img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Joins two images side by side, aligning them vertically at the center.
    
    - Pads the left image on the left if it's too narrow.
    - Pads the right image on the right if it's too narrow.
    """
    left_width, left_height = left_img.size
    right_width, right_height = right_img.size

    # Calculate vertical centering offsets
    left_offset = (target_height - left_height) // 2
    right_offset = (target_height - right_height) // 2

    # Create a blank white canvas
    combined = Image.new("RGB", (target_width * 2, target_height), "white")

    # Position left image (padded if needed)
    left_padded = Image.new("RGB", (target_width, target_height), "white")
    left_padded.paste(left_img, (target_width - left_width, left_offset))  # Align right within its section

    # Position right image (padded if needed)
    right_padded = Image.new("RGB", (target_width, target_height), "white")
    right_padded.paste(right_img, (0, right_offset))  # Align left within its section

    # Paste both onto the final canvas
    combined.paste(left_padded, (0, 0))
    combined.paste(right_padded, (target_width, 0))

    return combined

def process_booklets(pages: list, processed_dir: Path, ppb: int = 24, target_width: int = 1000, target_height: int = 1500):
    """Processes pages into booklets, grouping them in sets of `ppb` and pairing for booklet layout."""
    booklet_output_dir = processed_dir / "booklets"
    booklet_output_dir.mkdir(parents=True, exist_ok=True)

    total_pages = len(pages)
    current = 0

    for i in range(total_pages // ppb + (1 if total_pages % ppb != 0 else 0)):  # Iterate through booklets
        process = min(ppb, total_pages - (i * ppb))  # Pages left to process or ppb, whichever is less
        booklet_pages = []

        for j in range(process // 2):
            page_number = i * ppb + j
            partner_page = i * ppb + process - (j + 1)

            left_page = Image.open(pages[page_number])
            right_page = Image.open(pages[partner_page])

            if page_number % 2 == 0:
                combined_page = join_two_pages(left_page, right_page, target_width, target_height)
            else:
                combined_page = join_two_pages(right_page, left_page, target_width, target_height)

            output_filename = booklet_output_dir / f"booklet_{current:03}.jpg"
            combined_page.save(output_filename)
            booklet_pages.append(output_filename)
            print(f"Saved booklet page: {output_filename}")

            current += 1

    print(f"Finished processing booklets. Output in {booklet_output_dir}")
    return booklet_output_dir

def convert_booklets_to_pdf(booklet_output_dir: Path, output_pdf: Path):
    """Converts booklet images into a single PDF."""
    booklet_pages = sorted(booklet_output_dir.glob("*.jpg"))  # Adjust for PNG/WEBP if needed

    if not booklet_pages:
        print("No booklet images found to convert into PDF.")
        return

    images = [Image.open(page).convert("RGB") for page in booklet_pages]
    
    # Save as PDF
    pdf_path = output_pdf / "booklet.pdf"
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print(f"PDF saved: {pdf_path}")

def main():
    parser = argparse.ArgumentParser(description="Create booklets from processed pages.")
    parser.add_argument("--processed-dir", type=str, required=True, help="Directory containing processed pages")
    parser.add_argument("--start-pages-dir", type=str, required=True, help="Directory containing start pages")
    parser.add_argument("--end-pages-dir", type=str, required=True, help="Directory containing end pages")
    parser.add_argument("--page-height", type=int, default=1500, help="Height of output page images (default: 1500 pixels)")
    parser.add_argument("--page-width", type=int, default=1000, help="Width of output page images (default: 1000 pixels)")
    parser.add_argument("--ppb", type=int, default=24, help="Pages per booklet (default: 24)")

    args = parser.parse_args()

    # Collect all images in order after processing
    booklet_images = create_booklets(
        Path(args.processed_dir), 
        Path(args.start_pages_dir), 
        Path(args.end_pages_dir), 
        args.page_width, 
        args.page_height
    )

    # Process pages into booklets
    booklet_output_dir = process_booklets(booklet_images, Path(args.processed_dir), args.ppb, args.page_width, args.page_height)

    # Convert booklet pages to PDF
    convert_booklets_to_pdf(booklet_output_dir, Path(args.processed_dir))
    
if __name__ == "__main__":
    main()