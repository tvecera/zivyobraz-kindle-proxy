from PIL import Image
import requests
from flask import Flask, send_file
from urllib.parse import urlencode
import io
import os
import yaml
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='./logs/zivyobraz-proxy.log', filemode='a')

# Initialize Flask app
app = Flask(__name__)


def validate_config(config):
    """Validate the structure and values of the configuration."""

    logging.info("Config validation....")

    required_keys = ['zivyobraz', 'devices']
    zivyobraz_keys = ['api_base_url']
    devices_keys = ['name', 'endpoint', 'mac', 'width', 'height', 'color_type', 'output_format', 'color_mode']

    # Validate required top-level keys
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required key '{key}' in configuration.")
            raise ValueError(f"Missing required key '{key}' in configuration.")

    # Validate nested keys and types
    for key in zivyobraz_keys:
        if key not in config['zivyobraz']:
            logging.error(f"Missing required key 'zivyobraz.{key}' in configuration.")
            raise ValueError(f"Missing required key 'zivyobraz.{key}' in configuration.")

    for key in devices_keys:
        for device_item in config['devices']:
            if key not in device_item:
                logging.error(f"Missing required key 'devices.{key}' in configuration.")
                raise ValueError(f"Missing required key 'devices.{key}' in configuration.")

    for device_item in config['devices']:
        if device_item['color_type'] not in ['BW', '3C', '4G', '7C']:
            logging.error(f"Invalid 'device.color_type' value ['BW', '3C', '4G', '7C'].")
            raise ValueError(f"Invalid 'device.color_type' value ['BW', '3C', '4G', '7C'].")

        if device_item['output_format'] not in ['JPEG', 'BMP', 'WEBP', 'PNG']:
            logging.error(f"Invalid 'device.output_format' value ['JPEG', 'BMP', 'WEBP', 'PNG'].")
            raise ValueError(f"Invalid 'device.output_format' value ['JPEG', 'BMP', 'WEBP', 'PNG'].")

        if device_item['color_mode'] not in ['L', 'RGB', 'CMYK']:
            logging.error(f"Invalid 'device.color_mode' value ['L', 'RGB', 'CMYK'].")
            raise ValueError(f"Invalid 'device.color_mode' value ['L', 'RGB', 'CMYK'].")


def load_config(filename):
    """Load and validate configuration from a YAML file."""

    logging.info(f"Try to load config file {filename}....")

    if not os.path.exists(filename):
        logging.error(f"Configuration file '{filename}' not found.")
        raise FileNotFoundError(f"Configuration file '{filename}' not found.")

    with open(filename, 'r') as file:
        try:
            result = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            logging.error(f"Error parsing YAML file: {exc}")
            raise ValueError(f"Error parsing YAML file: {exc}")

    validate_config(result)
    return result


# Set up argument parsing
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-c', '--config', type=str, help='Path to the configuration file',
                    default='./config/zivyobraz-proxy.yml')

# Parse arguments
args = parser.parse_args()

# Load configuration
loaded_config = load_config(args.config)

ZIVYOBLAZ_API_BASE_URL = loaded_config['zivyobraz']['api_base_url']


def convert_image(bmp_data, device_config):
    """
    Convert BMP data to grayscale PNG.
    :param device_config: Configuration dictionary for the device.
    :param bmp_data: Byte data of the BMP image.
    :return: Byte data of the converted PNG image.
    """
    with Image.open(io.BytesIO(bmp_data)) as img:
        final_img = img.convert(device_config['color_mode'])
        with io.BytesIO() as output:
            final_img.save(output, format=device_config['output_format'], bits=8)
            return output.getvalue()


def get_mime_type(image_format):
    """
    Get the MIME type for a given image format.

    :param image_format: The image format (e.g., "JPEG", "BMP").
    :return: The corresponding MIME type as a string.
    """
    format_to_mime = {
        "JPEG": "image/jpeg",
        "BMP": "image/bmp",
        "WEBP": "image/webp",
        "PNG": "image/png"
    }

    return format_to_mime.get(image_format.upper(), "application/octet-stream")


# Function to serve the image for a specific device
def serve_device_image(device_config):
    """
    Serve a converted and processed image for a specific device.
    :param device_config: Configuration dictionary for the device.
    :return: PNG image or error message with status code.
    """

    logging.info("Serve device image from the ZivyObraz API.")

    params = {
        'mac': device_config['mac'],
        'timestamp_check': 1,
        'x': device_config['width'],
        'y': device_config['height'],
        'c': device_config['color_type'],
        'fw': 1
    }

    url = f"{ZIVYOBLAZ_API_BASE_URL}?{urlencode(params)}"
    response = requests.get(url)

    if response.status_code == 200:
        logging.info(f"Successfully downloaded BMP image for {device_config['name']}.")
        png_data = convert_image(response.content, device_config)
        return send_file(io.BytesIO(png_data), mimetype=get_mime_type(device_config['output_format']))
    else:
        logging.error(f"Error downloading BMP image for {device_config['name']}, HTTP code: {response.status_code}")
        return f"Error downloading BMP image for {device_config['name']}, HTTP code: {response.status_code}", 500


# Dynamically create endpoints for each device
for device in loaded_config['devices']:
    app.add_url_rule(device['endpoint'], device['name'], lambda d=device: serve_device_image(d))

if __name__ == '__main__':
    # Run the Flask app on all interfaces on the specified port
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
