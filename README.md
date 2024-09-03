# Naver Image Downloader

A web application for downloading images from Naver Post and compressing them into a ZIP file.

## Features
- Download images from Naver Post URLs.
- Compress downloaded images into a ZIP file.

## How to Run
1. **Clone the Repository**
   ```bash
   git clone https://github.com/username/naver-image-downloader.git
   cd naver-image-downloader

2. **Install Dependencies**
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt

3. Run the Application
   ```bash
   python scripts/app.py
   
  Access the application in your browser at `http://127.0.0.1:5000`.

## How to Use
- Open the web application in your browser.
- Enter the Naver article URL in the provided form.
- Click the "Download" button to start the download process.
- Once the process is complete, the ZIP file will be downloaded automatically.

## Technologies Used
This project utilizes a combination of modern technologies and frameworks to achieve its functionality. Here’s a brief overview of what’s used:

### Programming Languages
- **Python**: The primary language used for the backend, leveraging its extensive libraries and frameworks to handle asynchronous tasks and web requests.

### Frameworks and Libraries
- **Flask**: A lightweight WSGI web application framework used to build the web interface of the application.
- **aiohttp**: A library for asynchronous HTTP requests, used to handle image downloads concurrently.
- **BeautifulSoup**: A library for parsing HTML and XML documents, used to scrape web content and extract data.


## Contributing
If you want to contribute, please create issues or pull requests on GitHub.

## License
This project is licensed under the [MIT License](LICENSE).
