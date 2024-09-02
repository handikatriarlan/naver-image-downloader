from flask import Flask, request, jsonify, render_template
import asyncio
from downloader import download_images_from_naver
import threading
import os

# Tentukan folder tempat index.html berada
template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__, template_folder=template_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({'message': 'No URL provided'}), 400

    def run_download():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(download_images_from_naver(url))
        except Exception as e:
            print(f'An error occurred: {e}')

    # Run download in a separate thread
    thread = threading.Thread(target=run_download)
    thread.start()

    return jsonify({'message': 'Download started!'})

if __name__ == '__main__':
    app.run(debug=True)
