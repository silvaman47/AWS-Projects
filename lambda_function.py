import json
import boto3
import urllib.parse
from PIL import Image
import io

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Get source bucket and key from S3 event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    dest_bucket = 'new-resized-image'  # Replace with your destination bucket
    
    try:
        # Get image from source bucket
        response = s3_client.get_object(Bucket=source_bucket, Key=key)
        image_data = response['Body'].read()
        
        # Resize image to 200x200
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((200, 200), Image.LANCZOS)
        
        # Save resized image to buffer
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        
        # Upload resized image to destination bucket
        dest_key = f"resized/{key}"
        s3_client.put_object(
            Bucket=dest_bucket,
            Key=dest_key,
            Body=buffer,
            ContentType='image/jpeg'
        )
        
        print(f"Successfully resized {key} and uploaded to {dest_bucket}/{dest_key}")
        return {
            'statusCode': 200,
            'body': json.dumps('Image resized successfully')
        }
    
    except Exception as e:
        print(f"Error processing {key}: {str(e)}")
        raise e
