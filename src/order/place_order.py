import requests


def admin_login(username, password):
    """发送管理员登录POST请求"""
    login_url = "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/Login.html"

    # 使用Session保持会话
    session = requests.Session()

    # 先GET页面获取fstoken（重要！）
    print("正在获取登录页面...")
    get_response = session.get(login_url)

    # 从页面HTML中提取fstoken
    import re

    fstoken_match = re.search(r'name="fstoken"\s+value="([^"]+)"', get_response.text)
    if not fstoken_match:
        # 尝试其他可能的格式
        fstoken_match = re.search(r'id="fstoken"\s+value="([^"]+)"', get_response.text)

    if fstoken_match:
        fstoken = fstoken_match.group(1)
        print(f"成功获取fstoken: {fstoken}")
    else:
        print("警告：未找到fstoken，尝试硬编码值")
        fstoken = "I2KnGUJOHIhd"  # 您提供的值

    # 构建POST数据（字段名需要根据实际表单调整）
    post_data = {
        "mail": username,
        "phrase": password,
        "fstoken": fstoken,
        "login.x": "34",
        "login.y": "4",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": login_url,
    }

    print(f"正在提交登录请求...")
    response = session.post(login_url, data=post_data, headers=headers, allow_redirects=True)

    print(f"响应状态码: {response.status_code}")
    print(f"最终URL: {response.url}")

    # 判断是否登录成功
    if response.url == "https://www.tokyokawaiilife.jp/fs/lizlisaadmin/MyPageTop.html":
        print("✓ 登录成功")
    else:
        print("✗ 登录失败， 响应内容片段:", response.text[:500])

    return response


# 使用示例
if __name__ == "__main__":
    # 替换为您的实际用户名和密码
    USERNAME = "charismafight@hotmail.com"
    PASSWORD = "7u82enpa"

    response = admin_login(USERNAME, PASSWORD)

# https://www.tokyokawaiilife.jp/fs/lizlisaadmin/163-5108-0
