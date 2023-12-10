# ZivyObraz proxy

## Introduction

This project serves as a simple proxy for integrating Kindle devices with Zivyobraz.eu. It efficiently converts BMP
images fetched from the Zivyobraz.eu API into formats suitable for the Kindle KT3 screensaver.

It dynamically creates endpoints for different devices and serves images in various formats like JPEG, BMP, WebP,
and PNG.

## Features

- Supports multiple image formats.
- Dynamic endpoint creation for various devices.
- Docker support for easy deployment and scalability.

## Requirements

- Python 3.9 or higher
- Flask
- Pillow
- Requests
- PyYAML

## Running with Docker on Raspberry Pi (ARM 64)

To run the script using Docker on a Raspberry Pi:

1. Create directories:
    - `zivyobraz-kindle-proxy/config`
    - `zivyobraz-kindle-proxy/logs`
2. Copy the modified `zivyobraz-proxy.yml` configuration into the `config` directory.
3. In the `zivyobraz-departures` directory, run the Docker container using the command:

   ```
   docker run -d --name kindle-proxy --restart=always -p 8080:8080 -e PORT=8080 -v ./config:/usr/src/app/config -v ./logs:/usr/src/app/logs ghcr.io/tvecera/zivyobraz-kindle-proxy:$VERSION
   ```

## Building and Running Your Own Local Docker Image

1. Clone the repository:
   ```
   git clone https://github.com/tvecera/zivyobraz-kindle-proxy.git
   cd zivyobraz-kindle-proxy
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application:
    - Edit `config/zivyobraz-proxy.yml` to set device configurations and API endpoints.

4. Run the application:
   ```
   python proxy.py
   ```

## Docker Setup

To run the application in a Docker container:

1. Build the Docker image:
   ```
   docker build -t zivyobraz-kindle-proxy:latest .
   ```

2. Run the Docker container:
    - On default port 8080:
      ```
      docker run -d --name kindle-proxy --restart=always -p 8080:8080 -v ./config:/usr/src/app/config -v ./logs:/usr/src/app/logs zivyobraz-kindle-proxy:latest
      ```
    - On a custom port (e.g., 8081):
      ```
      docker run -d --name kindle-proxy --restart=always -p 8081:8081 -e PORT=8081 -v ./config:/usr/src/app/config -v ./logs:/usr/src/app/logs zivyobraz-kindle-proxy:latest
      ```

## Usage

Access the application via `http://localhost:8080/images/kindle.png` or the configured port.

## License

[MIT License](LICENSE)

## Links

- [Živý obraz](https://zivyobraz.eu/)