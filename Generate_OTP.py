import boto3
import json
import re
import base64
from datetime import datetime, timedelta
import string
import random

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = "otpstore"  # Replace with your DynamoDB table name
otp_expiry_minutes = 2  # Expiry time changed to 2 minutes
token_length = 6  # OTP length (number of digits)

table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Log the full event for debugging
        print("Received event:", json.dumps(event))

        # Ensure request body is extracted correctly
        body = event.get("body", None)

        if body is None:
            return response_error(422, "Request body is missing")

        # Decode Base64 if required (for API Gateway compatibility)
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode("utf-8")

        print("Decoded Body:", body)

        # Parse the JSON request body
        try:
            body_json = json.loads(body)
        except json.JSONDecodeError:
            return response_error(400, "Invalid JSON format in request body")

        print("Parsed Body:", body_json)

        # Extract email
        email = body_json.get("email", "").strip()
        print(f"Extracted email: {email}")

        if not email:
            return response_error(422, "Required field 'email' not found or invalid")

        # Validate email format
        if not is_valid_email(email):
            return response_error(422, "Invalid email address format")

        # Generate OTP
        otp = generate_random_string(token_length, only_numbers=True)
        expiry_time = int((datetime.utcnow() + timedelta(minutes=otp_expiry_minutes)).timestamp())

        # Store OTP in DynamoDB
        item = {
            "email": email,  # ✅ Partition key
            "otp": otp,
            "expiryAt": expiry_time  # ✅ For TTL
        }

        table.put_item(Item=item)

        return response_success({
            "message": "OTP generated successfully",
            "data": {
                "otp": otp
            }
        })

    except Exception as error:
        print(f"Error: {str(error)}")
        return response_error(500, f"OTP generation failed: {str(error)}")

# Helper function for error responses
def response_error(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"message": message})
    }

# Helper function for success responses
def response_success(data):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(data)
    }

# Validate email format using regex
def is_valid_email(email):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

# Generate a random OTP
def generate_random_string(length, only_numbers=False):
    characters = string.digits if only_numbers else string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
