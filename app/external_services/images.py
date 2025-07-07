from typing import List
import requests
import os
from urllib.parse import urlparse
from app.utils.parsing import sanitize_filename
import time


def download_image_bytes(url: str) -> bytes:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url, 
                headers=headers,
                timeout=30,
                stream=True,
                verify=True
            )
            response.raise_for_status()
            return response.content
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"Timeout on attempt {attempt + 1}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise Exception(f"Timeout after {max_retries} attempts")
            
        except requests.exceptions.ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Connection error on attempt {attempt + 1}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise Exception(f"Connection failed after {max_retries} attempts: {str(e)}")
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                raise Exception(f"Access forbidden (403) - Image may be protected: {url}")
            elif response.status_code == 404:
                raise Exception(f"Image not found (404): {url}")
            else:
                raise Exception(f"HTTP Error {response.status_code}: {str(e)}")
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Unexpected error on attempt {attempt + 1}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise Exception(f"Failed to download image after {max_retries} attempts: {str(e)}")

def upload_img_from_url(url: str, filename: str, game_prefix: str,s3_service) -> str:
    clean_filename = sanitize_filename(filename)
    clean_game_prefix = sanitize_filename(game_prefix)
    
    if not clean_filename.endswith('.png'):
        clean_filename += '.png'
    
    try:
        image_bytes = download_image_bytes(url)
        result = s3_service.upload_from_bytes(image_bytes, clean_filename, clean_game_prefix)
        if not result["success"]:
            raise Exception(f"S3 upload failed: {result['error']}")
        return f"https://teodiodocker-images.s3.us-east-2.amazonaws.com/{result['object_key']}"
    except Exception as e:
        print(f"Failed to process image from {url}: {str(e)}")
        raise