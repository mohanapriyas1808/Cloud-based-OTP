import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('otpstore')  

def lambda_handler(event, context):
    """
    Lambda function to verify OTP sent by the user.
    """
    try:
      
        print("Received event: " + json.dumps(event))
        
        # Extract parameters from the body field of the event
        body = json.loads(event.get('body', '{}'))
        otp_received = body.get('otp')  # OTP value received for verification
        email_received = body.get('email')  # Email received for verification

        
        if not otp_received or not email_received:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing OTP or Email in the request')
            }

      
        print(f"Received verification request for OTP: {otp_received} with Email: {email_received}")

        
        response = table.get_item(
            Key={'otp': otp_received}  # Use OTP as the partition key to look up the item
        )

        
        if 'Item' in response:
            stored_otp = response['Item']['otp']
            stored_email = response['Item']['email']
            expiry_at = response['Item']['expiryAt']

            print(f"Stored OTP: {stored_otp}, Stored Email: {stored_email}, Expiry: {expiry_at}")

            
            current_time = int(datetime.utcnow().timestamp())
            if current_time > expiry_at:
                return {
                    'statusCode': 400,
                    'body': json.dumps('OTP has expired')
                }

      
            if stored_otp == otp_received and stored_email == email_received:
                return {
                    'statusCode': 200,
                    'body': json.dumps('OTP Verified Successfully!')
                }
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps('Invalid OTP or Email')
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('OTP not found in the database')
            }

    except ClientError as e:
        print(f"Error verifying OTP: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
