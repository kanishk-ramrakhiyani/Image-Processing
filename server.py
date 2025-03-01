import os
import uuid
import asyncio
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from DatabaseHelper import save_request, get_request_status,delete_request_status
from Image_processor import process_csv

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class RequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        """Handle file upload (Fixed Multipart Handling)."""
        if self.path == "/upload":
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid content type"}).encode())
                return

            boundary = content_type.split("boundary=")[-1]
            if not boundary:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing boundary"}).encode())
                return

            # Read and decode the request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8", errors="ignore")

            # Extract CSV file content
            file_start = body.find("\r\n\r\n") + 4
            file_end = body.rfind(f"--{boundary}--") - 2
            if file_start < 4 or file_end < 0:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid file upload"}).encode())
                return

            csv_content = body[file_start:file_end]

            # Validate CSV before proceeding
            success_count, failure_count, errors = asyncio.run(process_csv(csv_content, None, validate_only=True))

            # If all rows fail, reject the request
            if success_count == 0 and failure_count >= 0:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "CSV validation failed", "details": errors}).encode())
                return

            # Generate request ID only if at least one row is valid
            request_id = str(uuid.uuid4())
            save_request(request_id, "processing")

            # Process CSV asynchronously (only valid rows)
            success_count, failure_count, errors = asyncio.run(process_csv(csv_content, request_id))

            response_body = {
                "request_id": request_id,
                "success_count": success_count,
                "failure_count": failure_count
            }

            # Correct status codes
            if success_count == 0:
                self.send_response(400)  # No successful rows at all
            elif failure_count > 0:
                self.send_response(206)  # Some rows failed
            else:
                self.send_response(200)  # All rows succeeded

            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_body).encode())

    def do_GET(self):
        """Check request status."""
        if self.path.startswith("/status/"):
            request_id = self.path.split("/")[-1]
            status = get_request_status(request_id)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": status}).encode())


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    """Run server."""
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
