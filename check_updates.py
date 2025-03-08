import requests
from bs4 import BeautifulSoup
import time

MAX_RETRIES = 3

def check_update(anchor_url, processed_audio, blacklist):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.ximalaya.com',
        'Upgrade-Insecure-Requests': '1'
    }
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(anchor_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            latest_audio = soup.find('div', class_='new-audio-container')
            if latest_audio:
                audio_name = latest_audio.find('a').text.strip()
                audio_url = latest_audio.find('a')['href']
                audio_url = f"https://www.ximalaya.com{audio_url}"  # 补全 URL
                if audio_name not in processed_audio and audio_name not in blacklist:
                    print(f"Found new audio: {audio_name}")
                    return audio_name, audio_url
            break
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Request failed. Retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(5)
            else:
                print(f"Failed to fetch {anchor_url} after {MAX_RETRIES} attempts: {e}")
    return None, None
