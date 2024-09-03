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
        return None, None
    
    # Membuat folder sementara untuk menyimpan gambar
    temp_folder = os.path.join(desired_path, f'{title}_temp')
    os.makedirs(temp_folder, exist_ok=True)
    print(f"Images will be saved to: {temp_folder}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f'Error {response.status} while accessing {url}')
                return None, None
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
                    else:
                        print(f"Error string does not include 'src' {linkdata}")
                except (IndexError, ValueError) as e:
                    print(f'Error parsing linkdata: {e}')
            
            if tasks:
                await asyncio.gather(*tasks)
    
    zip_path = os.path.join(desired_path, f'{title}.zip')
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(temp_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_folder)
                zipf.write(file_path, arcname)
    
    for root, dirs, files in os.walk(temp_folder, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_folder)
    
    print(f'Images have been zipped and saved to: {zip_path}')
    return title, zip_path

async def download(session, picture_url, picture_path):
    async with session.get(picture_url) as r:
        if r.status == 200:
            with open(picture_path, 'wb') as file:
                file.write(await r.read())
            print(f'Downloaded {picture_url}')
        else:
            print(f'Error {r.status} while getting request for {picture_url}')

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

def main():
    urlinput = input('Enter post URL: ')
    asyncio.run(download_images_from_naver(urlinput))

if __name__ == '__main__':
    main()
