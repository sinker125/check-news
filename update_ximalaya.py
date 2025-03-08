import requests
import os
import time

# 专辑 ID
ALBUM_ID = '51001379'
# 获取专辑音频列表接口（pageSize设置足够大以一次获取全部数据）
TRACK_LIST_URL = f"https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={ALBUM_ID}&pageNum=1&pageSize=100&sort=-1"

# 存储更新内容的文件（每一行格式：标题&&播放URL）
TXT_FILE = "new_updates.txt"

# 黑名单：出现在此集合中的音频标题将不写入（也可以根据 trackId 做过滤）
BLACKLIST = {"黑名单内容1", "黑名单内容2"}

# 为了防止被认为爬虫，设置标准的 User-Agent 和请求间延时
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def get_existing_titles():
    """读取文件中已存在的音频标题（用于判断新旧）"""
    if not os.path.exists(TXT_FILE):
        return set()
    with open(TXT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    existing = set()
    for line in lines:
        parts = line.strip().split("&&")
        if parts:
            existing.add(parts[0])
    return existing

def fetch_tracks():
    """获取专辑内所有音频信息"""
    resp = requests.get(TRACK_LIST_URL, headers=HEADERS)
    data = resp.json()
    tracks = data.get("data", {}).get("tracks", [])
    return tracks

def get_audio_url(track_id):
    """获取单个音频的真实播放 URL"""
    audio_api = f"https://www.ximalaya.com/revision/play/v1/audio?ptype=1&id={track_id}"
    resp = requests.get(audio_api, headers=HEADERS)
    data = resp.json()
    return data.get("data", {}).get("src", "")

def main():
    existing_titles = get_existing_titles()
    tracks = fetch_tracks()
    new_entries = []

    for track in tracks:
        title = track.get("title", "").strip()
        # 如果标题在黑名单中或已经存在，则跳过
        if title in BLACKLIST or title in existing_titles:
            continue

        # 从 track.url 中提取 trackId（一般格式为 /sound/{trackId}）
        track_url = track.get("url", "")
        track_id = track_url.rstrip('/').split('/')[-1]
        
        audio_src = get_audio_url(track_id)
        if audio_src:
            new_entries.append(f"{title}&&{audio_src}")
        else:
            print(f"Warning: 未获取到音频 [{title}] 的真实播放 URL。")
        # 延时 1 秒，防止请求过快
        time.sleep(1)
    
    if new_entries:
        # 追加新内容到文件中
        with open(TXT_FILE, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(entry + "\n")
        print(f"Added {len(new_entries)} new entries.")
    else:
        print("No new tracks found (可能全部为旧内容或已在黑名单中)。")

if __name__ == "__main__":
    main()
