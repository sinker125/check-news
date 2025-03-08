import requests
import os
import time

# ------------------------------
# 配置部分
# ------------------------------

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://www.ximalaya.com/"
}

# 文件路径
NEW_UPDATES_FILE = "new_updates.txt"
BLACKLIST_FILE = "blacklist.txt"
ALBUM_FILE = "author.txt"

# ------------------------------
# 辅助函数
# ------------------------------

def load_blacklist():
    """读取黑名单文件，返回需要过滤的音频标题集合"""
    if not os.path.exists(BLACKLIST_FILE):
        return set()
    with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def get_existing_titles():
    """读取已存在的音频标题，用于判断新旧内容"""
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
    """从 ALBUM_FILE 中读取订阅的专辑链接"""
    if not os.path.exists(ALBUM_FILE):
        print(f"{ALBUM_FILE} 文件不存在，请先创建并写入专辑链接。")
        return []
    with open(ALBUM_FILE, "r", encoding="utf-8") as f:
        albums = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return albums

def fetch_album_tracks(album_id, page=1, page_size=100):
    """获取专辑内的音频列表"""
    url = f"https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page}&pageSize={page_size}&sort=-1"
    print(f"请求专辑接口：{url}")
    resp = requests.get(url, headers=HEADERS)
    print(f"状态码：{resp.status_code}")
    print("响应内容预览：", resp.text[:200])
    try:
        data = resp.json()
    except Exception as e:
        print(f"解析专辑 {album_id} 的 JSON 时出错：{e}。响应内容：{resp.text}")
        return []
    tracks = data.get("data", {}).get("tracks", [])
    return tracks

def get_audio_url(track_id):
    """获取单个音频的真实播放 URL"""
    url = f"https://www.ximalaya.com/revision/play/v1/audio?ptype=1&id={track_id}"
    print(f"请求音频接口：{url}")
    resp = requests.get(url, headers=HEADERS)
    try:
        data = resp.json()
    except Exception as e:
        print(f"解析音频 {track_id} 的 JSON 时出错：{e}。响应内容：{resp.text}")
        return ""
    src = data.get("data", {}).get("src", "")
    print(f"返回的音频 URL: {src}")
    return src

# ------------------------------
# 主逻辑
# ------------------------------

def main():
    existing_titles = get_existing_titles()
    blacklist_titles = load_blacklist()
    album_links = read_albums()
    if not album_links:
        print("没有订阅的专辑，请在 author.txt 中添加专辑链接。")
        return

    new_entries = []

    for album_link in album_links:
        album_id = album_link.rstrip('/').split('/')[-1]
        print(f"处理专辑：{album_link} (album_id={album_id})")
        tracks = fetch_album_tracks(album_id)
        if not tracks:
            print(f"  没有找到专辑 {album_link} 的音频信息。")
            continue

        for track in tracks:
            title = track.get("title", "").strip()
            if title in blacklist_titles:
                print(f"  跳过黑名单中的音频：{title}")
                continue
            if title in existing_titles:
                print(f"  音频已存在，跳过：{title}")
                continue
            track_url = track.get("url", "")
            if not track_url:
                continue
            track_id = track_url.rstrip('/').split('/')[-1]
      
