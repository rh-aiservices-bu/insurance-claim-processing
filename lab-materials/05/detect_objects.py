import os
import requests
import json

from process_image import process_image

detection_endpoint = os.environ.get("DETECTION_ENDPOINT")
claims_endpoint = os.environ.get("CLAIMS_ENDPOINT")

def download_images(claim_id):
    claim_endpoint = claims_endpoint + f"/db/claims/{claim_id}"
    claim_info = requests.get(claim_endpoint).json()
    images = claim_info["original_images"]
    
    downloaded_images = []
    failed_downloads = []
    
    for image in images:
        image_name = image["image_name"]
        image_key = image["image_key"]
        image_endpoint = claims_endpoint + f"/images/{image_key}"
        
        response = requests.get(image_endpoint)
        
        if response.status_code == 200:
            content_type = response.headers['Content-Type']
            if content_type == 'binary/octet-stream':
                with open(f"{image_name}", 'wb') as file:
                    file.write(response.content)
                print(f'Saved image {image_name}.')
            else:
                print(f"Unexpected content type: {content_type}")
                failed_downloads.append(image_name)
        else:
            print(f"Failed to retrieve image {image_name}. Status code: {response.status_code}")
            failed_downloads.append(image_name)
        
        downloaded_images.append(image_name)
        
    if failed_downloads:
        raise Exception(f"Not all images were downloaded. Successfully downloaded these: {downloaded_images}\nFailed to download these: {failed_downloads}")
        
    return downloaded_images

def upload_images(claim_id, images):
    upload_endpoint = claims_endpoint + f"/db/claims/{claim_id}/processed_image"
    
    for image in images:
        files = {'image': (image, open(image, 'rb'), 'image/jpeg')}
        response = requests.post(upload_endpoint, files=files)
    
def process_images(images):
    processed_images = []
    for image in images:
        processed_image = process_image(image, detection_endpoint)
        processed_images.append(processed_image)
    return processed_images

def detect_objects(claim_id = None):
    claim_id = claim_id or int(os.environ.get("claim_id"))
    
    downloaded_images = download_images(claim_id)
    processed_images = process_images(downloaded_images)
    upload_images(claim_id, processed_images)

def batch_detect_objects(claim_ids = None):
    if not claim_ids:
        with open('claims.json') as f:
            claim_ids = json.load(f)["claim_ids"]
            
    print(f"processing claims: {claim_ids}")
    
    for claim_id in claim_ids:
        detect_objects(claim_id)

if __name__ == '__main__':
    batch_detect_objects()