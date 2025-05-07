import boto3
import json
from botocore.exceptions import ClientError

# Initialize SES client and DynamoDB resource
ses = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')

# SES sender email (must be verified in SES)
from_address = 'mohanaads18@gmail.com'

# DynamoDB table
table_name = "otpstore"
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Lambda function to process DynamoDB stream events and send OTP emails using SES.
    """
    try:
        print("Full event received: " + json.dumps(event))
        
        # Check if 'Records' key exists in the event (required for DynamoDB stream event)
        if 'Records' not in event:
            raise ValueError("Invalid event format: Missing 'Records' key.")
        
        # Process each record in the event
        for record in event['Records']:
            if record.get('eventName') in ['INSERT', 'MODIFY']:  # Process both INSERT and MODIFY events
                new_image = record['dynamodb'].get('NewImage', {})
                print(f"NewImage: {json.dumps(new_image)}")

                # Extract email and OTP from DynamoDB record
                email = new_image.get('email', {}).get('S')
                otp = new_image.get('otp', {}).get('S')

                if email and otp:
                    print(f"Sending OTP {otp} to {email}")
                    send_email(otp, email)
                else:
                    print(f"Missing email or OTP in record. Email: {email}, OTP: {otp}")

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "OTP processing failed",
                "error": str(e)
            })
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "OTP emails processed successfully."
        })
    }

def send_email(otp, to_address):
    """
    Send an OTP email using AWS SES.
    """
    html_body = f"""
    <html>
        <body>
            <p>Use this code to verify your login at Simple OTP:</p>
            <h1>{otp}</h1>
        </body>
    </html>
    """
    plain_body = f"Use this code to verify your login at Simple OTP: {otp}"

    params = {
        'Destination': {
            'ToAddresses': [to_address],
        },
        'Message': {
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': html_body,
                },
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': plain_body,
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Your OTP at Simple OTP',
            }
        },
        'Source': from_address,
    }

    try:
        # Send email using SES
        response = ses.send_email(**params)
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending email: {e}")
        raise e  # Reraise the error to capture it in the main Lambda function
