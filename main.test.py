import requests

# 国内需要代理
proxies = {
    "http": "http://127.0.0.1:10808",  # HTTP代理
    "https": "http://127.0.0.1:10808",  # HTTPS代理
}

url = "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/161-1002-0"

response = requests.get(url, proxies=proxies)
print(response.status_code)
