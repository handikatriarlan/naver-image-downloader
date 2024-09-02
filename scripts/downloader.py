import os
import aiohttp
import asyncio
import json
import re
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup

async def download_images_from_naver(url):
    # Menentukan jalur folder di "C:\Users\handi\Downloads"
    title, desired_path = await get_page_title_and_folder(url)
    
    # Membuat folder jika belum ada
    os.makedirs(desired_path, exist_ok=True)
    print(f"Images will be saved to: {desired_path}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f'Error {response.status} while accessing {url}')
                return
            text = await response.text()
            tasks = []
            for item in text.split("data-linkdata=\'")[1:]:
                try:
                    linkdata = json.loads(item.split("\'>\n")[0])
                    if 'src' in linkdata:
                        picture_url = linkdata['src']
                        picture_id = unquote(os.path.basename(urlparse(picture_url).path))
                        # Hapus karakter yang tidak diinginkan dari nama file
                        picture_id = re.sub(r'%\d{2}', '', picture_id)  # Hapus %2D, %28, dsb
                        picture_id = re.sub(r'[<>:"/|?*]', '', picture_id)  # Hapus karakter khusus
                        # Format nama file baru dengan urutan gambar
                        picture_name = f'{os.path.splitext(picture_id)[0]}{os.path.splitext(picture_id)[1]}'
                        picture_path = os.path.join(desired_path, picture_name)
                        if not os.path.isfile(picture_path):
                            tasks.append(download(session, picture_url, picture_path))
                    else:
                        print(f"Error string does not include 'src' {linkdata}")
                except (IndexError, ValueError) as e:
                    print(f'Error parsing linkdata: {e}')
            
            if tasks:
                await asyncio.gather(*tasks)

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
            title = soup.title.string.strip()  # Mengambil judul dari tag <title>
            # Menentukan nama folder berdasarkan judul
            title = re.sub(r'[<>:"/|?*]', '', title)  # Membersihkan karakter khusus
            desired_path = os.path.join(r'C:\Users\handi\Downloads', title)
            return title, desired_path

def main():
    urlinput = input('Enter post URL: ')
    asyncio.run(download_images_from_naver(urlinput))

if __name__ == '__main__':
    main()
