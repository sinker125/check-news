import requests
from bs4 import BeautifulSoup
import os
import time

# 读取主播列表
def read_anchor_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# 读取已处理的音频信息
def read_processed_audio(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.split('&&')[0] for line in file.readlines()]
    return []

# 检查主播是否有更新
def check_update(anchor_url, processed_audio):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(anchor_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 这里需要根据喜马拉雅网页结构调整选择器
        latest_audio = soup.find('div', class_='latest-audio-class')  # 示例选择器，需调整
        if latest_audio:
            audio_name = latest_audio.find('a').text.strip()
            if audio_name not in processed_audio:
                audio_url = latest_audio.find('a')['href']
                return audio_name, audio_url
    except Exception as e:
        print(f"Error checking {anchor_url}: {e}")
    return None, None

# 写入更新信息到文件
def write_updates(updates, file_path):
    if not updates:
        return
    with open(file_path, 'a', encoding='utf-8') as file:
        for name, url in updates:
            file.write(f"{name}&&{url}\n")

def main():
    anchor_list_file = 'anchor_list.txt'
    update_file = 'update_info.txt'
    anchors = read_anchor_list(anchor_list_file)
    processed_audio = read_processed_audio(update_file)
    new_updates = []

    for anchor in anchors:
        audio_name, audio_url = check_update(anchor, processed_audio)
        if audio_name and audio_url:
            new_updates.append((audio_name, audio_url))
        time.sleep(5)  # 每个请求间隔 5 秒

    write_updates(new_updates, update_file)

if __name__ == "__main__":
    main()
