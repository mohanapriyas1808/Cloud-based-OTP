import boto3
import json
import re
from datetime import datetime, timedelta
import string
import random


dynamodb = boto3.resource('dynamodb')

table_name = "otpstore"  # Replace with your DynamoDB table name
otp_expiry_minutes = 5  # Hardcoded expiry time in minutes
token_length = 6  # Default OTP length (number of digits)


table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
    
        print("Received event: " + json.dumps(event))
        
      
        body = json.loads(event.get("body", "{}"))
        email = body.get("email")
        print(f"Extracted email: {email}")  # Log the extracted email
        
        
        if not email:
            print("Email not found or invalid")
            return {
                "statusCode": 422,
                "body": json.dumps({
                    "message": "Required field email not found or invalid"
                })
            }
        
        if not is_valid_email(email):
            print("Invalid email address format")
            return {
                "statusCode": 422,
                "body": json.dumps({
                    "message": "Invalid email address"
                })
            }
        
      
        otp = generate_random_string(token_length, only_numbers=True)
        expiry_time = int((datetime.utcnow() + timedelta(minutes=otp_expiry_minutes)).timestamp())

        
        item = {
            "otp": otp,  # Use OTP as the partition key
            "email": email,
            "expiryAt": expiry_time  # Store expiry time
        }
        
  
        table.put_item(Item=item)

      
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "OTP generated",
                "data": {
                    "otp": otp  # Return OTP directly
                }
            })
        }
    
    except Exception as error:
      
        print(f"Error: {str(error)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "OTP generation failed",
                "error": str(error)
            })
        }

def is_valid_email(email):
    """
    Validate email address using regular expression.
    """
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return re.match(email_regex, email) is not None

def generate_random_string(length, only_numbers=False):
    """
    Generate a random string of specified length.
    If only_numbers is True, the string will consist of digits only.
    """
    characters = string.digits if only_numbers else string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
