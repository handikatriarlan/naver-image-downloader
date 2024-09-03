from flask import Flask, render_template, request, send_file, jsonify
import asyncio
import os
from downloader import download_images_from_naver

template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__, template_folder=template_folder)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        title, zip_file_path = loop.run_until_complete(download_images_from_naver(url))
        
        if not title or not zip_file_path:
            return jsonify({'message': 'Error during download process.'}), 500
        
        return send_file(zip_file_path, as_attachment=True, download_name=os.path.basename(zip_file_path))
    
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'message': 'Download completed!'})

if __name__ == '__main__':
    app.run(debug=True)
