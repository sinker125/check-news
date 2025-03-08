import requests
import os
import time

# ------------------------------
# 配置部分
# ------------------------------

# 用于防爬虫：设置标准的 User-Agent
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

# 存储更新内容的文件，每行格式：标题&&播放URL
NEW_UPDATES_FILE = "new_updates.txt"
# 黑名单：这里的内容（可以是音频标题或其它标识）将被过滤掉，不更新
BLACKLIST = {"示例黑名单内容1", "示例黑名单内容2"}

# 专辑列表文件（每行写一个你想更新的专辑链接，例如：https://www.ximalaya.com/album/51001379）
ALBUM_FILE = "author.txt"

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

def read_albums():
    """
    从 ALBUM_FILE 中读取订阅的专辑链接（每行一个链接，例如：
    https://www.ximalaya.com/album/51001379）
    """
    if not os.path.exists(ALBUM_FILE):
        print(f"{ALBUM_FILE} 文件不存在，请先创建并写入专辑链接。")
        return []
    with open(ALBUM_FILE, "r", encoding="utf-8") as f:
        # 去除空行和注释（以 # 开头的行）
        albums = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return albums

def fetch_album_tracks(album_id, page=1, page_size=100):
    """
    获取专辑内的音频列表
    接口示例：
    https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page}&pageSize={page_size}&sort=-1
    """
    url = f"https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page}&pageSize={page_size}&sort=-1"
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()
    except Exception as e:
        print(f"Error decoding JSON for album {album_id}: {e}. Response: {resp.text}")
        return []
    tracks = data.get("data", {}).get("tracks", [])
    return tracks

def get_audio_url(track_id):
    """
    获取单个音频的真实播放 URL
    接口示例：
    https://www.ximalaya.com/revision/play/v1/audio?ptype=1&id={track_id}
    """
    url = f"https://www.ximalaya.com/revision/play/v1/audio?ptype=1&id={track_id}"
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()
    except Exception as e:
        print(f"Error decoding JSON for track {track_id}: {e}. Response: {resp.text}")
        return ""
    return data.get("data", {}).get("src", "")

# ------------------------------
# 主逻辑
# ------------------------------

def main():
    existing_titles = get_existing_titles()
    album_links = read_albums()
    if not album_links:
        print("没有订阅的专辑，请在 author.txt 中添加专辑链接。")
        return

    new_entries = []

    # 遍历每个专辑链接
    for album_link in album_links:
        # 提取 album_id，假设 URL 格式为：https://www.ximalaya.com/album/51001379
        album_id = album_link.rstrip('/').split('/')[-1]
        print(f"处理专辑：{album_link} (album_id={album_id})")
        # 获取该专辑内的音频列表（这里只取第一页）
        tracks = fetch_album_tracks(album_id)
        if not tracks:
            print(f"  没有找到专辑 {album_link} 的音频信息。")
            continue

        for track in tracks:
            title = track.get("title", "").strip()
            # 过滤：如果标题在黑名单中或已经存在，则跳过
            if title in BLACKLIST or title in existing_titles:
                continue
            # 从 track.url 中提取 track_id（一般格式为 /sound/{track_id}）
            track_url = track.get("url", "")
            track_id = track_url.rstrip('/').split('/')[-1]
            audio_src = get_audio_url(track_id)
            if audio_src:
                entry = f"{title}&&{audio_src}"
                new_entries.append(entry)
                print(f"  新增：{title}")
            else:
                print(f"  警告：获取音频 [{title}] 播放 URL 失败。")
            # 延时 1 秒防止请求过快
            time.sleep(1)
        # 专辑之间也加延时
        time.sleep(1)

    if new_entries:
        with open(NEW_UPDATES_FILE, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(entry + "\n")
        print(f"共新增 {len(new_entries)} 条更新记录。")
    else:
        print("没有发现新更新。")

if __name__ == "__main__":
    main()
