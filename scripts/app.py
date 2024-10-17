from flask import Flask, render_template, request, jsonify, send_file
import asyncio
from downloader import download_images_from_naver
import os

# Set template folder to find index.html correctly
template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

app = Flask(__name__, template_folder=template_folder)

# Define the path for downloads (for sending files to the user, not saving on server)
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Ensure the downloads directory exists (to temporarily store ZIP files)
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Route to display the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle image downloading
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return jsonify({"message": "Please provide a valid URL."})
    
    # Async function to handle downloading images from Naver
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(download_images_from_naver(url))
    
    if 'zip_file' in result:
        zip_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], result['zip_file'])
        if os.path.exists(zip_file_path):
            return jsonify({
                "message": "Images downloaded successfully!",
                "zip_file": result["zip_file"]
            })
        else:
            return jsonify({"message": "File not found."})
    else:
        return jsonify({"message": result["message"]})

# Route to serve the ZIP file for download
@app.route('/downloads/<filename>', methods=['GET'])
def download_zip(filename):
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)  # Sends file as attachment (downloadable)
    else:
        return "File not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
