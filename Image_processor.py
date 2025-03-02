import csv
import io
import os
import asyncio
import shutil
from Webhook import trigger_webhook
import requests
from PIL import Image
from DatabaseHelper import update_request_status, delete_request_status, insert_image_link

UPLOADS_DIR = "uploads/"
STATIC_DIR = "static/"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)


async def download_and_compress(url, request_id, index):
    """Download and compress an image, saving it with structured naming."""
    url = url.strip()
    if not url:
        return "error"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=10, allow_redirects=True)
        response.raise_for_status()

        # Validate if response is an image
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            return "error"

        # Create request-specific folder
        request_folder = os.path.join(UPLOADS_DIR, request_id)
        os.makedirs(request_folder, exist_ok=True)

        # Structured file naming
        file_name = f"{request_id}-{index}.jpg"
        output_path = os.path.join(request_folder, file_name)

        with open(output_path, "wb") as f:
            f.write(response.content)

        # Compress the image
        with Image.open(output_path) as img:
            img.save(output_path, "JPEG", quality=50)

        return f"/uploads/{request_id}/{file_name}"

    except requests.RequestException:
        return "error"
    except Exception:
        return "error"


async def process_csv(csv_content, request_id, validate_only=False):
    """Process CSV file: Validate, download, and compress images."""
    try:
        processed_rows = []
        errors = []
        reader = csv.DictReader(io.StringIO(csv_content))

        required_fields = ["Serial Number", "Product Name", "Input Image Urls"]

        if not reader.fieldnames or not all(field in reader.fieldnames for field in required_fields):
            return 0, 0, [
                "Invalid CSV format. Missing required columns: 'Serial Number', 'Product Name', 'Input Image Urls'."]

        reader.fieldnames = [name.strip() for name in reader.fieldnames]


        tasks = []
        valid_rows = []
        success_count = 0
        failure_count = 0
        image_counter = 1  # Track sequential numbering

        for index, row in enumerate(reader, start=1):
            if not all(row.get(field, "").strip() for field in required_fields):
                errors.append(f"Row {index}: Missing required field(s).")
                failure_count += 1
                continue

            input_urls = row["Input Image Urls"].strip()
            input_urls_list = [url.strip() for url in input_urls.split(",") if url.strip()]

            if not input_urls_list:
                errors.append(f"Row {index}: No valid image URLs provided.")
                failure_count += 1
                continue

            valid_rows.append((row, input_urls_list))

            if not validate_only:
                tasks.append(asyncio.gather(*[
                    download_and_compress(url, request_id, i + image_counter) for i, url in enumerate(input_urls_list)
                ]))
                image_counter += len(input_urls_list)

        if validate_only:
            return len(valid_rows), failure_count, errors

        if not valid_rows:
            return 0, failure_count, errors  # Reject entire CSV if all rows are invalid

        results = await asyncio.gather(*tasks)

        # Create processed CSV only if there are valid images

        processed_csv_path = os.path.join(STATIC_DIR, f"{request_id}.csv")

        with open(processed_csv_path, mode="w", newline="") as csvfile:
            fieldnames = reader.fieldnames + ["Processed Image URLs"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for (row, input_urls), output_urls in zip(valid_rows, results):
                filtered_urls = [url for url in output_urls if url != "error"]
                row["Processed Image URLs"] = ",".join(filtered_urls)
                writer.writerow(row)
                try:
                    insert_image_link(
                        request_id,
                        row["Serial Number"],
                        row["Product Name"],
                        row["Input Image Urls"],
                        row["Processed Image URLs"]
                        )
                except Exception as e:
                    errors.append(f"Database insertion error for row {row.get('Serial Number')}: {str(e)}")

                success_count += len(filtered_urls)
                failure_count += len(output_urls) - len(filtered_urls)

        update_request_status(request_id, "completed")
        trigger_webhook(request_id,success_count,failure_count)
        return success_count, failure_count, errors
    except Exception:
        # delete_request_status(request_id)
        # print(UPLOADS_DIR)
        # print(request_id)
        #
        # request_folder = os.path.join(UPLOADS_DIR, request_id)
        # print(request_folder)
        # if os.path.exists(request_folder):
        #     shutil.rmtree(request_folder)  # ✅ Delete the entire folder safely

        return 0, 0, ["CSV or URL Validation failed"]  # ✅ Correct return type

