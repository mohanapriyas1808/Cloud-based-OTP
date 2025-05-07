import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('otpstore')  # Replace with your actual DynamoDB table name

def lambda_handler(event, context):
    """
    Lambda function to verify OTP sent by the user.
    """
    try:
        print("Received event:", json.dumps(event))
        
        # Extract request body safely
        body = json.loads(event.get('body', '{}'))
        otp_received = body.get('otp')
        email_received = body.get('email')

        if not otp_received or not email_received:
            return response_error(400, "Missing OTP or Email in the request")

        print(f"Received verification request for OTP: {otp_received} with Email: {email_received}")

        # Query DynamoDB using email (Partition key)
        response = table.get_item(Key={'email': email_received})

        if "Item" in response:
            stored_otp = response["Item"]["otp"]
            expiry_at = response["Item"]["expiryAt"]

            print(f"Stored OTP: {stored_otp}, Expiry: {expiry_at}")

            # Check if OTP is expired
            current_time = int(datetime.utcnow().timestamp())
            if current_time > expiry_at:
                return response_error(400, "OTP has expired")

            # Check if OTP matches
            if stored_otp == otp_received:
                return response_success({"message": "OTP Verified Successfully!"})
            else:
                return response_error(400, "Invalid OTP")

        else:
            return response_error(404, "OTP not found for the provided email")

    except ClientError as e:
        print(f"Error verifying OTP: {str(e)}")
        return response_error(500, "Internal Server Error")

# ✅ **CORS Fix - Structured API Responses**
def response_success(data):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",  # ✅ Fix for CORS
            "Access-Control-Allow-Methods": "OPTIONS, POST",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(data)
    }

def response_error(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",  # ✅ Fix for CORS
            "Access-Control-Allow-Methods": "OPTIONS, POST",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({"message": message})
    }
