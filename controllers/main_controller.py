import asyncio
import utils.parser as parser
from utils.parser import scrape
import aioshutil
from aiofiles import os as async_os
import os
from typing import List


async def file_move_by_tag(filename: str, tag: str) -> None:
    filename = os.path.split(filename)
    if not os.path.exists(os.path.join(filename[0], tag)): os.mkdir(os.path.join(filename[0], tag))
    await aioshutil.move(os.path.join(filename[0], filename[1]), os.path.join(filename[0], tag, filename[1]))


async def file_sorting(filename: str, fav_tags: List[str]) -> None:
    # files = list(filter(lambda x: os.path.splitext(x)[-1], os.listdir(directory)))
    is_found = False
    moved_tag = "err"
    res = await scrape(filename)
    if filename.endswith('.webp'):
        filename = os.path.splitext(filename)[0] + '.jpg'
    if not res:
        await file_move_by_tag(filename, "err")
    else:
        title_name = res[1] if res[1] else 'unknown'
        author = res[2] if res[2] else 'unknown'
        is_found = False
        for fav_tag in fav_tags:
            if " " not in fav_tag:
                if fav_tag in res[0] and not is_found:
                    is_found = True
                    await file_move_by_tag(filename, fav_tag)
                    moved_tag = f"[{title_name},{author}] {fav_tag}"
                    break
            else:
                many_fav_tags = fav_tag.split(" ")
                if set(many_fav_tags).issubset(res[0]):
                    many_fav_tags = " ".join(many_fav_tags)
                    is_found = True
                    await file_move_by_tag(filename, many_fav_tags)
                    moved_tag = f"[{title_name},{author}] {many_fav_tags}"
                    break
    if is_found:
        print(f'Файл - {os.path.basename(filename)} перемещен в {moved_tag} ≧◠‿◠≦✌')
        return
    else:
        print(f'Файл - {os.path.basename(filename)} перемещен в {moved_tag} ( ˘︹˘ )')
        return


async def folder_sorting(folder: str = "E:\\SortArts\\Phone\\VK\\webp") -> None:
    tags = [
        "loli", "double_anal", "solo anal_insertion", "solo anal", "full_nelson anal", "anal masturbation",
        "anal_masturbation", "anal_fingering", "anal", "spread_anus", "gaping", "fellatio", "blowjob", "paizuri",
        "tekoki", "solo masturbation", "huge_breasts sex", "large_breasts sex", "sex", "anus", "sling_swimsuit nipples",
        "bikini nipples", "nipple_tweak", "solo huge_breasts nipples", "solo large_breasts nipples", "lactation",
        "solo nipples", "nipples", "sling_swimsuit", "huge_breasts bikini", "large_breasts bikini", "bikini",
        "side-tie_panties", "solo ass", "ass_focus", "solo huge_breasts", "solo large_breasts", "solo breasts",
        "solo thick_thighs", "large_breasts thick_thighs", "large_breasts underwear", "underwear", "thick_thighs",
        "undressing", "animated", "swimsuit", "swimsuits", "bikini", "butt_plug", "ass_grab", "spread_ass", "huge_ass",
        "ass", "breasts", "nude", "no_bra", "thighs", "solo", "towel", "maid", "bunny_girl", "tagme", "absurdres",
        "topless", "kitsune", "breast_hold", "thighhighs"
    ]
    files = [os.path.join(folder, i) for i in filter(lambda x: os.path.splitext(x)[-1], os.listdir(folder))]
    for file in files:
        await file_sorting(file, tags)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(folder_sorting())

