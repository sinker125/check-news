import requests
import os
import time

# ------------------------------
# 配置部分
# ------------------------------

# 用于防爬虫：设置 User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# 存储更新内容的文件，每行格式：标题&&播放URL
NEW_UPDATES_FILE = "new_updates.txt"
# 黑名单：这里的内容（可用标题或 trackId）将被过滤掉，不更新；可自行扩展
BLACKLIST = {"示例黑名单内容1", "示例黑名单内容2"}

# 订阅播主列表文件，每行写一个播主 uid（比如 7712455）
AUTHOR_FILE = "author.txt"

# ------------------------------
# 辅助函数
# ------------------------------

def get_existing_titles():
    """读取文件中已存在的音频标题，用于判断新旧内容"""
    if not os.path.exists(NEW_UPDATES_FILE):
        return set()
    with open(NEW_UPDATES_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    existing = set()
    for line in lines:
        parts = line.strip().split("&&")
        if parts:
            existing.add(parts[0])
    return existing

def read_authors():
    """从 author.txt 中读取订阅的播主 uid（每行一个）"""
    if not os.path.exists(AUTHOR_FILE):
        print(f"{AUTHOR_FILE} 文件不存在，请先创建并写入播主 uid。")
        return []
    with open(AUTHOR_FILE, "r", encoding="utf-8") as f:
        # 去除空行和注释（以 # 开头）
        authors = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return authors

def fetch_author_albums(author_uid, page=1, page_size=50):
    """
    获取播主的专辑列表
    接口示例：https://www.ximalaya.com/revision/author/v1/getAlbumList?uid={uid}&pageNum={page}&pageSize={page_size}
    """
    url = f"https://www.ximalaya.com/revision/author/v1/getAlbumList?uid={author_uid}&pageNum={page}&pageSize={page_size}"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    albums = data.get("data", {}).get("albums", [])
    return albums

def fetch_album_tracks(album_id, page=1, page_size=100):
    """
    获取专辑内的音频列表
    接口示例：https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page}&pageSize={page_size}&sort=-1
    """
    url = f"https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page}&pageSize={page_size}&sort=-1"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    tracks = data.get("data", {}).get("tracks", [])
    return tracks

def get_audio_url(track_id):
    """
    获取单个音频的真实播放 URL
    接口示例：https://www.ximalaya.com/revision/play/v1/audio?ptype=1&id={track_id}
    """
    url = f"https://www.ximalaya.com/revision/play/v1/audio?ptype=1&id={track_id}"
    resp = requests.get(url, headers=HEADERS)
    data = resp.json()
    return data.get("data", {}).get("src", "")

# ------------------------------
# 主逻辑
# ------------------------------

def main():
    existing_titles = get_existing_titles()
    authors = read_authors()
    if not authors:
        print("没有订阅的播主，请在 author.txt 中添加播主 uid。")
        return

    new_entries = []

    # 遍历每个播主
    for uid in authors:
        print(f"处理播主：{uid}")
        # 默认只取第一页的专辑列表，也可以根据需要遍历更多页
        albums = fetch_author_albums(uid)
        if not albums:
            print(f"播主 {uid} 没有找到专辑信息。")
            continue

        for album in albums:
            album_id = album.get("albumId")  # 根据接口返回结构，专辑 id
            album_title = album.get("albumTitle", "").strip()
            print(f"  处理专辑：{album_title} ({album_id})")
            # 获取该专辑内的音频列表（这里只取第一页，按更新时间排序）
            tracks = fetch_album_tracks(album_id)
            for track in tracks:
                title = track.get("title", "").strip()
                # 过滤：标题在黑名单中或已存在则跳过
                if title in BLACKLIST or title in existing_titles:
                    continue
                # 从 track.url 中提取 track_id（一般格式为 /sound/{track_id}）
                track_url = track.get("url", "")
                track_id = track_url.rstrip('/').split('/')[-1]
                audio_src = get_audio_url(track_id)
                if audio_src:
                    entry = f"{title}&&{audio_src}"
                    new_entries.append(entry)
                    print(f"    新增：{title}")
                else:
                    print(f"    警告：获取音频 [{title}] 播放 URL 失败。")
                # 延时 1 秒，防止请求过快
                time.sleep(1)
            # 专辑间也可以加延时
            time.sleep(1)

    if new_entries:
        # 追加新内容到文件中
        with open(NEW_UPDATES_FILE, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(entry + "\n")
        print(f"共新增 {len(new_entries)} 条更新记录。")
    else:
        print("没有发现新更新。")

if __name__ == "__main__":
    main()
