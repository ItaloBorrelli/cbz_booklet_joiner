# **CBZ Processing and Booklet Creation**

This project provides a set of scripts to **extract, process, and format CBZ files** into printable booklets.  
It includes two main scripts:

1. **`cbz_processing.py`** – Extracts CBZ files, processes images (resizing, renaming, blank page handling).
2. **`create_booklets.py`** – Organizes images into booklet format and generates a **printable PDF**.

---

## **AUTHOR'S NOTE**

This was originally developed to create a printable PDF for volumes of One Piece without an official English volume yet released for personal use. The code was designed based on the way the CBZ files were organized. They may very well be organized differently in the material you are trying to print. I don't intend to update this for any reason, and if you'd like to make changes for your own purposes, you may iterate on this code.

Also, be sensible and don't commit any copyrighted material.

---

## **Prerequisites**

Make sure you have **Python 3** installed along with the required dependencies:

```sh
pip install pillow
```

---

## **1️⃣ Extract and Process CBZ Files**

### **Script:** `cbz_processing.py`

This script extracts **CBZ** files, renames images, adjusts page layouts, and converts formats.

### **Basic Usage**

Before running this script, make sure to **place your start pages** in the `start_pages` folder in the order they should appear in the book, naming them alphabetically to maintain the correct sequence. Similarly, place **end pages** in the `end_pages` folder in the order they should appear at the end, ensuring they are named alphabetically for proper sequencing.

```sh
python3 cbz_processing.py --input-dir cbz
```

- Extracts all CBZ files inside the `cbz/` folder into `cbz/extracted/`.

### **Options**

| Argument             | Description |
|----------------------|-------------|
| `--input-dir`       | The directory containing **CBZ** files. *(Required)* |
| `--no-swap-01`      | Comma-separated CBZ names that should **keep** `_01` and `_00` unchanged. Use `none` to allow all swaps, or `all` to prevent all swaps. |
| `--convert-format`  | Converts images to `jpg`, `png`, or `webp`. *(Default: `jpg`)* |

#### **Process CBZ files and convert to PNG**

```sh
python3 cbz_processing.py --input-dir cbz --no-swap-01 none --convert-format png
```

- Extracts **CBZ** files in `cbz/`
- Swaps `_01` and `_00` for **all** CBZs.
- Converts **all extracted images** to PNG.

---
### **Updated Sections for README**

Here’s how you can modify your README to include **Section 2 for organizing start and end pages** and move booklet creation to **Section 3**:

---

```md
---

## **2️⃣ Organize Start and End Pages**

Before creating a booklet, you need to **properly organize your start and end pages**.

- Place **start pages** in the `start_pages/` folder in the order they should appear.  
- Place **end pages** in the `end_pages/` folder in the order they should appear.  

### **Using `blank.png` for Custom Blank Pages**

If you want to **intentionally add blank pages** at specific locations, you can **copy `blank.png`** into your `start_pages/` or `end_pages/` directory and rename it accordingly.

#### **Example:**

If you want a blank page between **two intro pages**, organize your `start_pages/` folder like this:

```txt
start_pages/
├── 001_cover.png
├── 002_intro.png
├── 003_blank.png  # This will add an intentional blank page
├── 004_intro_2.png
```

This allows for greater **control over booklet formatting** before the main content.

### Size files with `convert.sh`

This script is written for 1000x1500, but can be alterted for your manga page sizes. It will scale the page down to ?x1460, add a 5px black border then add a background to fill the 1000x1500 space. It requires `ImageMagick` to be installed, and is used by providing an input file, output file and a hex background colour. If no background colour is provided, white is used. Example:

```bash
./convert.sh input.jpg output.jpg "#FCABED" # Ensure quotations are used around the hex value, otherwise bash considers this a comment
```

---

## **3️⃣ Create Printable Booklets**

### **Script:** `create_booklets.py`

This script **organizes images into booklets**, ensuring:

- **Start pages** are properly aligned and resized.
- **Processed pages** are added.
- **End pages** are appended.
- **Blank pages** are inserted to maintain a page count divisible by 4.
- **Pages are paired correctly** for booklet printing.
- **Outputs a final PDF**.

### **Basic Usage**

```sh
python3 create_booklets.py --processed-dir cbz/extracted --end-pages-dir cbz/end_pages --start-pages-dir cbz/start_pages
```

### **Options**

| Argument             | Description |
|----------------------|-------------|
| `--processed-dir`   | Directory containing extracted and processed pages. *(Required)* |
| `--start-pages-dir` | Directory containing **start pages** (e.g., cover, intro) in `start_pages/`. *(Required)* |
| `--end-pages-dir`   | Directory containing **end pages** (e.g., credits, back cover) in `end_pages/`. *(Required)* |
| `--page-height`     | Height of output pages in pixels. *(Default: `1500`)* |
| `--page-width`      | Width of output pages in pixels. *(Default: `1000`)* |
| `--ppb`            | Pages per booklet. *(Default: `24`)* |

### **Example Usage**

#### **Generate a 24-page booklet with 1500x1000 images**

```sh
python3 create_booklets.py --processed-dir cbz/extracted --end-pages-dir cbz/end_pages --start-pages-dir cbz/start_pages --page-height 1500 --page-width 1000 --ppb 24
```

- **Extracted images** are collected and resized.
- **Booklet pages are paired correctly**.
- **Blank pages are inserted** if needed.
- **A final `booklet.pdf` is generated**.

---

## **Final Output**

The final processed files are located in:

- `cbz/extracted/` – Processed images from CBZ files.
- `cbz/extracted/booklets/` – Final booklet pages, paired and formatted.
- `cbz/extracted/booklet.pdf` – The final printable PDF.

---

## **Printing**

When printing the final PDF, use the **double-sided** setting, flipping on the **short edge**.  
I recommend printing one [section/signature](https://en.wikipedia.org/wiki/Section_(bookbinding)) first to verify alignment before committing to a large batch. The pages will appear out of order, but once folded, they should be correct. Adjust the `ppb` value in `create_booklets.py` to change booklet thickness.

### **Saving Ink & Money**

To reduce printing costs, **identify pages with color** and print them separately while printing the rest in black & white.  
Make sure to print color pages in **pairs of two**, starting with an **odd-numbered page**.

#### **Example:**

If your booklet has **18 total pages**, and only pages **1 (cover) and 10** have color, print:

- **Color pages:** `1-2, 9-10`
- **Black & white pages:** `3-8, 11-18`

Always print double-sided, flipping on the short edge.

---

## **Understanding Folded Signatures**

When printing a booklet, the pages will not appear in order when viewed flat but will **align correctly when folded**.

Here’s a **visual example** of a folded signature layout (for an 8-page booklet):

```txt
Sheet 1 (Front)    | Sheet 1 (Back)
------------------- | -------------------
Page 8      Page 1 | Page 2      Page 7
Page 6      Page 3 | Page 4      Page 5
```

- **When folded, Page 1 will be the first page, and Page 8 will be the last.**
- **This ensures correct page order when binding.**

For best results, test with a small number of pages before printing an entire booklet.