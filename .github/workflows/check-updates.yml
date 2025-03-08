# .github/workflows/monitor_podcasts.yml
name: Podcast Update Monitor

on:
  schedule:
    - cron: '0 22 * * *'  # 北京时间每天6点（UTC+8时区）<button class="citation-flag" data-index="7">
  workflow_dispatch:      # 允许手动触发<button class="citation-flag" data-index="8">

jobs:
  check-updates:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4  # 确保获取最新代码<button class="citation-flag" data-index="7">

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'  # 固定Python版本<button class="citation-flag" data-index="9">

    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install requests==2.31.0 beautifulsoup4==4.12.3 fake-useragent==1.1.3
      # 依赖版本锁定保证稳定性<button class="citation-flag" data-index="3">

    - name: Execute monitoring script
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        python <<EOF
        # 注意：此处需严格保持缩进<button class="citation-flag" data-index="9">
        import os
        import re
        import time
        import random
        from fake_useragent import UserAgent
        from bs4 import BeautifulSoup
        import requests

        MONITOR_FILE = 'monitor_list.txt'
        OUTPUT_FILE = 'podcast_updates.txt'
        BLACKLIST_FILE = 'blacklist.txt'

        def read_config(file_path):
            try:
                with open(file_path, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                return []

        def get_session():
            ua = UserAgent()
            session = requests.Session()
            session.headers.update({
                'User-Agent': ua.random,
                'Referer': 'https://www.ximalaya.com/',
                'Accept-Language': 'zh-CN,zh;q=0.9'
            })
            return session

        def parse_audio_info(url):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    time.sleep(random.uniform(1, 3))
                    response = get_session().get(url, timeout=10)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 需根据实际DOM结构调整选择器<button class="citation-flag" data-index="7">
                    title = soup.select_one('.title').text.strip()
                    audio_url = soup.select_one('audio')['src']
                    return f"{title}&&{audio_url}"
                except Exception as e:
                    print(f"Attempt {attempt+1} failed: {e}")
                    if attempt == max_retries - 1:
                        return None

        def main():
            monitors = read_config(MONITOR_FILE)
            blacklist = read_config(BLACKLIST_FILE)
            existing = read_config(OUTPUT_FILE)
            
            new_updates = []
            for url in monitors:
                print(f"Checking: {url}")
                result = parse_audio_info(url)
                if result:
                    if result not in existing and not any(keyword in result for keyword in blacklist):
                        new_updates.append(result)
            
            if new_updates:
                with open(OUTPUT_FILE, 'a') as f:
                    f.write('\n' + '\n'.join(new_updates) + '\n')
                
                # 自动提交变更<button class="citation-flag" data-index="7">
                os.system('git config --global user.name "github-actions"')
                os.system('git config --global user.email "actions@github.com"')
                os.system(f'git commit -am "Add {len(new_updates)} new entries"')
                os.system(f'git push https://{os.environ["GITHUB_ACTOR"]}:{os.environ["GITHUB_TOKEN"]}@github.com/{os.environ["GITHUB_REPOSITORY"]}.git HEAD:main')

        if __name__ == '__main__':
            main()
        EOF

    - name: Check for failures
      if: ${{ failure() }}
      run: |
        echo "::error::脚本执行失败，请检查日志"
        exit 1  # 强制失败状态<button class="citation-flag" data-index="9">
