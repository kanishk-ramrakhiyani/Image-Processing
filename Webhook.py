import requests

# Replace this with the actual external webhook URL
WEBHOOK_URL = "https://external-service.com/webhook"

def trigger_webhook(request_id, success_count, failure_count, additional_data=None):
    """
    Triggers a webhook callback to an external endpoint after image processing is complete.

    Args:
        request_id (str): The unique request identifier.
        success_count (int): Number of successfully processed images.
        failure_count (int): Number of images that failed to process.
        additional_data (dict, optional): Any extra data to include in the payload.

    Returns:
        bool: True if the webhook was successfully triggered, False otherwise.
    """
    payload = {
        "request_id": request_id,
        "status": "completed",
        "success_count": success_count,
        "failure_count": failure_count
    }
    if additional_data:
        payload.update(additional_data)

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Webhook triggered successfully for request {request_id}")
        return True
    except Exception as e:
        print(f"Failed to trigger webhook for request {request_id}: {str(e)}")
        return False
