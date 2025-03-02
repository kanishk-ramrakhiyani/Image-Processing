# Image Processing System

A Python-based image processing system that accepts CSV file uploads containing product data and image URLs, downloads and compresses the images asynchronously, and stores processed data in a PostgreSQL database.

## Overview

This project implements an end-to-end solution for processing product data with associated images. It provides:

- An **Upload API** to accept CSV files and return a unique request ID.
- A **Status API** to check the processing status of each request.
- Asynchronous image downloading and compression.
- Storage of processed CSV data and image details in a PostgreSQL database.

## Features

- **CSV Upload & Validation:**  
  Accepts CSV files with required columns ("Serial Number", "Product Name", "Input Image Urls") and validates the content.

- **Asynchronous Image Processing:**  
  Uses `asyncio` to download and compress images concurrently. Processed images are stored in a request-specific folder.

- **Database Integration:**  
  Uses PostgreSQL (via `psycopg2`) to track processing requests and store processed image links along with product details.

- **API Endpoints:**
    - **Upload API (`/upload`):** Accepts file uploads and starts processing.
    - **Status API (`/status/{request_id}`):** Returns the current processing status for a given request ID.

- **Postman Collection:**  
  A publicly accessible Postman collection is provided for easy API testing.

## Technologies Used

- **Programming Language:** Python 3.x
- **Database:** PostgreSQL
- **Async Processing:** asyncio
- **HTTP Server:** Python's built-in `http.server`
- **Image Processing:** Pillow (PIL)
- **HTTP Requests:** requests
- **Database Driver:** psycopg2

## How to run

- **Ensure you have PostgreSQL installed and running.**
- **Create a database named image_processing (or modify DB_CONFIG in DatabaseHelper.py accordingly).**
- **Execute the following SQL scripts to create the necessary tables:**
```
CREATE TABLE requests (
id text PRIMARY KEY,
status text
);

CREATE TABLE public.image_links (
id serial PRIMARY KEY,
request_id text REFERENCES requests ON DELETE CASCADE,
serial_number integer,
product_name text,
input_image_urls text,
output_image_urls text
);
```
- **Modify the necessary user and password in databaseHelper.py or use existing credential settings as configured in DataBaseHelper.py.**
```
  DB_CONFIG = {
  "dbname": "image_processing",
  "user": "kanishk",
  "host": "localhost",
  "port": "5432",
  }
```
- **Navigate to Project Directory and run python3 server.py**
- **Upload the test.csv file in the project directory or use your own to send post request**
- **Uploaded and compressed images are kept in uploads directory and processed CSVs are kept in static folder**
- **The uploaded images are kept in a directory with the name of request id and inside it images are labelled as Request_id-1,Request_id-2 and so on**
- **Processed CSVs are kept in static directory with name Request-id.csv**
- **More information can be found in the detailed document.**