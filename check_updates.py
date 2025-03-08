import requests
from bs4 import BeautifulSoup
import os
import time

def read_anchor_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

def read_blacklist(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    return []

def read_processed_audio(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.split('&&')[0] for line in file.readlines()]
    return []

def check_update(anchor_url, processed_audio, blacklist):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.ximalaya.com',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        response = requests.get(anchor_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 主播主页最新音频选择器（需根据实际页面调整）
        latest_audio = soup.find('div', class_='user-podcast-item')
        if latest_audio:
            audio_name = latest_audio.find('a', class_='title').text.strip()
            audio_url = latest_audio.find('a', class_='title')['href']
            audio_url = f"https://www.ximalaya.com{audio_url}"  # 补全 URL
            
            if audio_name not in processed_audio and audio_name not in blacklist:
                print(f"Found new audio: {audio_name}")
                return audio_name, audio_url
    except Exception as e:
        print(f"Error checking {anchor_url}: {e}")
    return None, None

def write_updates(updates, file_path):
    if not updates:
        return
    with open(file_path, 'a', encoding='utf-8') as file:
        for name, url in updates:
            file.write(f"{name}&&{url}\n")

def main():
    anchor_list_file = 'anchor_list.txt'
    blacklist_file = 'blacklist.txt'
    update_file = 'update_info.txt'
    
    if not os.path.exists(update_file):
        with open(update_file, 'w', encoding='utf-8') as f:
            pass
    
    anchors = read_anchor_list(anchor_list_file)
    blacklist = read_blacklist(blacklist_file)
    processed_audio = read_processed_audio(update_file)
    new_updates = []

    for anchor in anchors:
        audio_name, audio_url = check_update(anchor, processed_audio, blacklist)
        if audio_name and audio_url:
            new_updates.append((audio_name, audio_url))
        time.sleep(5)  # 避免被反爬虫

    write_updates(new_updates, update_file)

if __name__ == "__main__":
    main()
