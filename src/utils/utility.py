from io import BytesIO
import os
import markdown2
from bs4 import BeautifulSoup
import subprocess
import platform
import time
from typing import Optional
import uuid
import pandas as pd
from PIL import Image
import math
import base64
import tiktoken
import pymupdf 
from dotenv import load_dotenv

from fastapi import (
    status,
    HTTPException,
)

load_dotenv()
tiktoken_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
embedding_cost_per_1k_tokens = float(
        os.getenv("OPENAI_EMBEDDING_MODEL_NAME_COST_1K_TOKENS")
    )
llm_cost_per_1k_input_tokens = float(
        os.getenv("OPENAI_MODEL_GPT4_COST_1K_INPUT_TOKENS")
    )
llm_cost_per_1k_output_tokens = float(
        os.getenv("OPENAI_MODEL_GPT4_COST_1K_OUTPUT_TOKENS")
    )

EXTRACTED_IMG_DIR = os.getenv("EXTRACTED_IMG_DIR", r"src\uploaded_file\extracted_img")
def create_new_id(prefix: Optional[str]):
    """Create a new unique id value

    Args:
        prefix (Optional[str]): 

    Returns:
        new_id: Unique id value
    """
    new_id = prefix + '-' + str(uuid.uuid4()) + str(int(time.time()))[-4:]
    return str(new_id)

def delete_file(file_path):
    # Check if file exists and is a file (not a directory)
    if os.path.exists(file_path):
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_path} was successfully deleted.")
                return True
            except PermissionError:
                print(f"Permission denied: Unable to delete file {file_path}.")
            except FileNotFoundError:
                print(f"File not found: {file_path}.")
            except Exception as e:
                print(f"An error occurred while trying to delete the file {file_path}: {e}")
        else:
            print(f"{file_path} is a directory, not a file.")
    else:
        print(f"The file {file_path} does not exist.")
    return False

def get_file_extension(file_name: str):
    return file_name.lower().split('.')[-1]

def define_column_name(data_df: pd.DataFrame):
    """Get specific column name of object_type, requirement_type, allocation, test_spec_col

    Args:
        data_df (pd.DataFrame):

    Returns:
        str, str, str: 
    """
    print("define_column_name data_df.columns", data_df.columns)
    object_type_col = next((i for i in data_df.columns if "objecttype" in i.lower()), None)
    requirement_type_col = next((i for i in data_df.columns if "requirementtype" in i.lower()), None)
    allocation_col = next((i for i in data_df.columns if "allocation" in i.lower()), None)
    test_spec_col = list(data_df.columns)[-1]
    columns_mapping = {
        "object_type": object_type_col,
        "requirement_type": requirement_type_col,
        "allocation": allocation_col,
        "test_specification": test_spec_col
    }
    return columns_mapping

def get_unique_string()->str:
    return str(uuid.uuid4()) + str(int(time.time()))[-4:]

def convert_image_to_base64(image_path):
    """
    Converts an image file (JPEG or PNG) to a Base64 string.

    Args:
        image_path (str): The file path to the image that you want to convert.

    Returns:
        str: The Base64 encoded string representation of the image, or
             None if an error occurs during the file reading or encoding process.

    Example usage:
        base64_string = convert_image_to_base64('path/to/your/image.jpeg')
        if base64_string:
            print(base64_string)  # This will print the Base64 string of the image
    """
    try:
        # Open the image file in binary mode
        with open(image_path, 'rb') as image_file:
            # Read the binary data
            binary_data = image_file.read()
            
            # Encode the binary data to Base64
            base64_encoded_data = base64.b64encode(binary_data)
            
            # Decode the Base64 bytes to a UTF-8 string
            base64_string = base64_encoded_data.decode('utf-8')
            
            return base64_string
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def convert_pdf_to_list_image(pdf_path):
    doc = pymupdf.open(pdf_path)
    images_base64 = []
    
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        images_base64.append(img_base64)

    return images_base64

def tokens_count_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = len(tiktoken_encoding.encode(string))
    return num_tokens

def tokens_count_from_image(image_path: str) -> float:
    """
    Calculate the number of tokens based on the size of an image.

    Args:
        image_path (str): The path to the image.

    Returns:
        float: The calculated number of tokens.
    """
    # Open the image and get its width and height
    with Image.open(image_path) as img:
        width, height = img.size

    # Tile size is 512 x 512 pixels
    tile_width = 512
    tile_height = 512

    # Calculate how many tiles are needed to cover the width and height
    tiles_along_width = math.ceil(width / tile_width)
    tiles_along_height = math.ceil(height / tile_height)

    # Calculate the total number of tiles
    total_tiles = tiles_along_width * tiles_along_height

    # Calculate the number of tokens
    num_tokens = 85 + 170 * total_tiles
    return num_tokens

def calculate_embedding_cost(input_string: str) -> float:
    count_tokens = tokens_count_from_string(input_string)
    embedding_cost = (embedding_cost_per_1k_tokens * count_tokens) / 1000
    return embedding_cost

def calculate_cost_for_llm_request(input_string: str, response_string: str, image_path = None) -> float:
    image_tokens = 0
    if image_path:
        image_tokens = tokens_count_from_image(image_path)

    input_tokens = tokens_count_from_string(input_string) + image_tokens
    response_tokens = tokens_count_from_string(response_string)
    llm_input_cost = (llm_cost_per_1k_input_tokens * input_tokens) / 1000
    llm_output_cost = (llm_cost_per_1k_output_tokens * response_tokens) / 1000

    return llm_input_cost + llm_output_cost

def get_filename_without_extension(file_path):
    # Extracts the base name from the file path
    base_name = os.path.basename(file_path) 

    # Splits the base name into name and extension
    file_name, _ = os.path.splitext(base_name)
    
    return file_name

def markdown_to_plain_text(md_text):
    # Convert markdown to HTML
    html = markdown2.markdown(md_text)
    # Parse HTML and get plain text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)
