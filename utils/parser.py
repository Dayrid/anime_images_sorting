import asyncio
import os
import aiohttp as aiohttp
import aiofiles as aiofiles
import regex as re

from aiofiles import os as async_os
from PIL import Image, UnidentifiedImageError

from bs4 import BeautifulSoup


async def fetch_file(file: str, session: aiohttp.ClientSession) -> str:
    handle = await aiofiles.open(file, mode='rb')
    # files = {"file": (file, handle)}
    form = aiohttp.FormData()
    form.add_field("file", await handle.read(), filename=file, content_type="text/plain")
    async with session.post("https://www.iqdb.org", data=form) as response:
        await handle.close()
        return await response.text()


async def fetch(url: str, session: aiohttp.ClientSession) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) '
                             'Chrome/24.0.1312.27 Safari/537.17'}
    async with session.get(url, headers=headers, proxy="http://bt8kf7xa:TFA1fZJi@91.209.31.176:49043") as response:
        return await response.text()


async def scrape(file: str) -> tuple:
    size = os.path.getsize(file)
    size /= 1024
    if size >= 8192:
        return tuple()

    if file.endswith(('.jpg', '.webp')):
        try:
            img = Image.open(file)
        except UnidentifiedImageError:
            return tuple()
        rgb_im = img.convert('RGB')
        rgb_im.save(os.path.splitext(file)[0] + '.jpg')
        del img, rgb_im

    if file.endswith('.webp'):
        await async_os.remove(file)
        file = os.path.splitext(file)[0] + '.jpg'

    async with aiohttp.ClientSession() as session:

        html = await fetch_file(file, session)
        res = await parse_urls(html)

        if res == "err":
            return tuple()

        used_url_count = 0

        title_name = None
        author = None
        tags = set()

        p = r"[^a-zA-Z0-9]+"
        for url in res:

            data = await booru_parsing(url, session)
            if title_name is None or re.search(p, title_name) is not None:
                title_name = data[1]

            if author is None or re.search(p, author) is not None:
                author = data[2]

            tags = tags.union(data[0])
            used_url_count += 1

            if used_url_count >= 2 and tags:
                break

        return tags, title_name, author


async def parse_urls(html: str):
    soup = BeautifulSoup(html, 'lxml')

    err = soup.find("div", class_="err")
    if err:
        return "err"

    nomatch = soup.find("div", class_="nomatch")
    if nomatch:
        return "err"

    urls = []
    tables = soup.find(id="pages").find_all("table")
    for table in tables[1:]:
        urls_lst = table.find_all("a")
        for url in urls_lst:
            urls.append(url.get("href"))

    urls = list(map(lambda x: "http://" + x.replace("https://", "").replace("http://", "").replace("//", ""), urls))
    return urls


async def booru_parsing(url: str, session: aiohttp.ClientSession) -> tuple:
    tags = set()
    title_name = None
    author = None

    html = await fetch(url, session)
    soup = BeautifulSoup(html, "lxml")

    if 'danbooru' in url:
        # tags, title_name, author = await danbooru(soup, tags)
        pass
    if 'konachan' in url:
        tags, title_name, author = await konachan(soup, tags, title_name, author)
    if 'sankaku' in url:
        tags, title_name, author = await sankaku(soup, tags, title_name, author)
    if 'yande.re' in url:
        tags, title_name, author = await yandere(soup, tags, title_name, author)
    if 'gelbooru' in url:
        tags, title_name, author = await gelbooru(soup, tags, title_name, author)
    if 'anime-pictures' in url:
        tags, title_name, author = await anime_pictures(soup, tags, title_name, author)
    data = (tags, title_name, author)
    return data


async def danbooru(soup: BeautifulSoup, tags: set = None) -> tuple:
    if tags is None:
        tags = set()
    author = soup.find('li', class_='tag-type-1')

    if author is not None:
        author = author['data-tag-name']

    title_name = soup.find('li', class_='tag-type-3')
    if title_name is not None:
        title_name = title_name['data-tag-name']

    # tags.extend([el['data-tag-name'] for el in soup.find_all('li', class_='tag-type-0')])
    for el in soup.find_all('li', class_='tag-type-0'):
        tags.add(el['data-tag-name'])

    return tags, title_name, author


async def konachan(soup: BeautifulSoup, tags: set = None, title_name: str = None, author: str = None) -> tuple:
    if tags is None:
        tags = set()

    if title_name is None:
        title_name = soup.find('li', class_="tag-link tag-type-title_name")
        if title_name is not None:
            title_name = title_name['data-name']

    if author is None:
        author = soup.find('li', class_="tag-link tag-type-artist")
        if author is not None:
            author = author['data-name']

    # tags.extend([el['data-name'] for el in soup.find_all('li', class_='tag-link tag-type-general')])
    tags = tags | {el['data-name'] for el in soup.find_all('li', class_='tag-link tag-type-general')}
    # for el in soup.find_all('li', class_='tag-link tag-type-general'):
    #     tags.add(el['data-name'])
    return tags, title_name, author


async def sankaku(soup: BeautifulSoup, tags: set = None, title_name: str = None, author: str = None) -> tuple:
    if tags is None:
        tags = list()

    new_tags = str(soup.find('title').text).replace(' | Sankaku Channel', '').split(', ')
    new_tags = [i.replace(' ', '_') for i in new_tags]
    tags.update(set(new_tags))

    if author is None:
        author = soup.find('li', class_='tag-type-artist')
        if author is not None:
            author = author.find('a')
            if author is not None:
                author = author.text.replace(' ', '_')

    if title_name is None:
        title_name = soup.find('li', class_='tag-type-title_name')
        if title_name is not None:
            title_name = title_name.find('a')
            if title_name is not None:
                title_name = title_name.text.replace(' ', '_')

    return tags, title_name, author


async def yandere(soup: BeautifulSoup, tags: set = None, title_name: str = None, author: str = None) -> tuple:
    if tags is None:
        tags = set()
    new_tags = soup.find('img', id='image')
    if new_tags is None:
        new_tags = []
    else:
        new_tags = new_tags.get('alt').split(' ')
    tags.update(set(new_tags))
    if author is None:
        temp_author = soup.find('li', class_='tag-type-artist')
        if temp_author is not None:
            author = temp_author.find_all('a')
            if author is not []:
                for a in temp_author:
                    try:
                        if a.text != "?":
                            author = a.text
                            break
                    except:
                        pass
    if title_name is None:
        temp_cr = soup.find('li', class_='tag-type-title_name')
        if temp_cr is not None:
            temp_cr = temp_cr.find_all('a')
            if temp_cr is not []:
                for a in temp_cr:
                    if a.text in new_tags:
                        title_name = a.text
                        break
    return tags, title_name, author


async def gelbooru(soup: BeautifulSoup, tags: set = None, title_name: str = None, author: str = None) -> tuple:
    if tags is None:
        tags = set()

    new_tags = soup.find('section', class_='image-container')
    if new_tags is None:
        new_tags = []
    else:
        new_tags = new_tags.get('data-tags')[1:-1].split(" ")
        tags.update(set(new_tags))
    if author is None:
        temp_author = soup.find('li', class_='tag-type-artist')
        if temp_author is not None:
            author = temp_author.find("a")
            if author is not None:
                try:
                    author = author.text.replace(" ", "_")
                except:
                    author = ''
            # author = temp_author.find_all('a')
            # if author is []:
            #     author = ''
            # else:
            #     for a in author:
            #         try:
            #             if a.text.replace(" ", "_") in new_tags:
            #                 author = a.text.replace(" ", "_")
            #                 break
            #         except:
            #             pass
    if title_name is None:
        temp_cr = soup.find('li', class_='tag-type-copyright')
        if temp_cr is not None:
            temp_cr = temp_cr.find_all('a')
            if temp_cr is not []:
                for a in temp_cr:
                    if a.text.replace(" ", "_") in new_tags:
                        title_name = a.text.replace(" ", "_")
                        break
    return tags, title_name, author


async def anime_pictures(soup: BeautifulSoup, tags: set = None, title_name: str = None, author: str = None) -> tuple:
    if tags is None:
        tags = list()
    temp_tags = soup.find('ul', class_='tags')

    if temp_tags is not None:
        new_tags = temp_tags.find_all("a")
        new_tags = [tag.text.replace(" ", "_") for tag in new_tags]
        tags.update(set(new_tags))

    if author is None:
        temp_author = soup.find('a', class_='artist')
        if temp_author is not None:
            author = temp_author.text.replace(" ", "_")

    if title_name is None:
        temp_cr = soup.find('a', class_='copyright')
        if temp_cr is not None:
            title_name = temp_cr.text.replace(" ", "_")

    return tags, title_name, author


# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     tasks = [loop.create_task(scrape(r"D:\YandexDisk\unknown_files\-5413376063075104699_121.jpg"))]
#     loop.run_until_complete(asyncio.wait(tasks))
