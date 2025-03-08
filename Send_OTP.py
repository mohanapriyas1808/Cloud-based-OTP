import boto3
import json


ses = boto3.client('ses')
from_address = 'mohanaads18@gmail.com'  


dynamodb = boto3.resource('dynamodb')

table_name = "otpstore"  


table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Lambda function to process DynamoDB stream events and send OTP emails using AWS SES.
    """
    try:
        # Ensure 'Records' key exists in the event
        if 'Records' not in event:
            raise ValueError("Invalid event format: Missing 'Records' key.")

        for record in event['Records']:
            # Check for valid DynamoDB 'INSERT' events
            if record.get('eventName') == 'INSERT' and 'dynamodb' in record:
                # Extract data from the NewImage
                new_image = record['dynamodb'].get('NewImage', {})
                
                # Debug print to see the structure of the NewImage
                print(f"NewImage: {new_image}")
                
                # Extract OTP from 'pk' and email from 'email' field
                otp = new_image.get('otp', {}).get('S')  # Now looking for 'pk' for OTP
                to_address = new_image.get('email', {}).get('S')  # Extract email if available

                if otp and to_address:
                    print(f"Preparing to send OTP {otp} to {to_address}")
                    send_email(otp, to_address)
                else:
                    print(f"Missing 'otp' or 'email' in DynamoDB record. OTP: {otp}, Email: {to_address}")

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"message": "OTP generation failed", "error": str(e)})
        }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"message": "OTP emails processed successfully."})
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
        response = ses.send_email(**params)
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise
