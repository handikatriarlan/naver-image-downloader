import os
import aiohttp
import asyncio
import json
import re
import zipfile
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

async def download_images_from_naver(url):
    title, desired_path = await get_page_title_and_folder(url)

    if not title or not desired_path:
        return {"message": "Failed to get title or path."}
    
    # Membuat folder sementara untuk menyimpan gambar
    temp_folder = os.path.join(desired_path, f'{title}_temp')
    os.makedirs(temp_folder, exist_ok=True)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {"message": f"Error {response.status} while accessing the URL."}

            text = await response.text()
            tasks = []
            for item in text.split("data-linkdata=\'")[1:]:
                try:
                    linkdata = json.loads(item.split("\'>\n")[0])
                    if 'src' in linkdata:
                        picture_url = linkdata['src']
                        picture_id = unquote(os.path.basename(urlparse(picture_url).path))
                        picture_id = re.sub(r'%\d{2}', '', picture_id)
                        picture_id = re.sub(r'[<>:"/|?*]', '', picture_id)
                        picture_name = f'{os.path.splitext(picture_id)[0]}{os.path.splitext(picture_id)[1]}'
                        picture_path = os.path.join(temp_folder, picture_name)
                        if not os.path.isfile(picture_path):
                            tasks.append(download(session, picture_url, picture_path))
                except (IndexError, ValueError):
                    continue
            
            if tasks:
                await asyncio.gather(*tasks)
            else:
                return {"message": "No images found on the page."}

    # Membuat file ZIP dari gambar yang sudah diunduh
    zip_file_name = f'{title}.zip'
    zip_path = os.path.join(desired_path, zip_file_name)
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(temp_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_folder)
                zipf.write(file_path, arcname)

    # Menghapus file gambar setelah di-zip
    for root, dirs, files in os.walk(temp_folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_folder)

    return {"zip_file": zip_file_name}

async def download(session, picture_url, picture_path):
    async with session.get(picture_url) as r:
        if r.status == 200:
            with open(picture_path, 'wb') as file:
                file.write(await r.read())

async def get_page_title_and_folder(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f'Error {response.status} while accessing {url}')
            text = await response.text()
            soup = BeautifulSoup(text, 'html.parser')
            title = soup.title.string.strip()
            title = re.sub(r'[<>:"/|?*]', '', title)
            home_dir = os.path.expanduser('~')
            desired_path = os.path.join(home_dir, 'Downloads')
            return title, desired_path
