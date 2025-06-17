import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import hashlib
import json
import random
import time
import os



# 从环境变量中读取账号密码及推送接口信息
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
PUSHPLUS_TOKEN = os.getenv('PUSHPLUS_TOKEN')
BARK_URL = os.getenv('BARK_URL')
TX_APIKEY = os.getenv('TIANAPI_KEY')
SEMESTER_START = datetime(2025, 2, 23)  # 学期开始日期（周日）
USE_GROUP_PUSH = True  # 是否推送到 PushPlus 群组
GROUP_TOPIC = '12'  # 填入你的群组 topic
# 推送开关（由布尔值控制）
ENABLE_PUSHPLUS = True  # 控制是否启用 PushPlus 推送
ENABLE_BARK = True       # 控制是否启用 Bark 推送

if not USERNAME or not PASSWORD:
    raise ValueError("❌ 请在.env文件中配置 USERNAME 和 PASSWORD")
if not TX_APIKEY:
    print("⚠️ 未配置天气API密钥，天气功能不可用")
period_time_map = {
    '1-2': '08:00 - 09:50',
    '3-4': '10:10 - 12:00',
    '5-6': '14:30 - 16:20',
    '7-8': '16:30 - 18:20',
    '9-10': '19:30 - 21:30',
}

def get_current_week(start_date):
    today = datetime.now().date()
    return (today - start_date.date()).days // 7 + 1

# 会话登录获取 salt
session = requests.Session()
login_url = 'https://jwxt.bjwlxy.cn/eams/loginExt.action'
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': login_url,
    'Origin': 'https://jwxt.bjwlxy.cn',
    'Content-Type': 'application/x-www-form-urlencoded'
}
resp_login_page = session.get(login_url, headers=headers)
soup = BeautifulSoup(resp_login_page.text, 'html.parser')
salt = None
for script in soup.find_all('script'):
    if script.string and 'CryptoJS.SHA1' in script.string:
        match = re.search(r"CryptoJS\.SHA1\(['\"](.+?)['\"]\s*\+", script.string)
        if match:
            salt = match.group(1)
            break
if not salt:
    raise RuntimeError("❌ 未能从登录页面提取 salt")

encrypted_pwd = hashlib.sha1((salt + PASSWORD).encode('utf-8')).hexdigest()

data = {
    'username': USERNAME,
    'pwd': encrypted_pwd,
    'language': 'on',
    'session_locale': 'zh_CN'
}

try:
    resp = session.post(login_url, data=data, headers=headers, timeout=10)
except Exception as e:
    print(f"❌ 登录请求失败：{e}")
    course_map = {i: [] for i in range(7)}
else:
    if '用户名或密码' in resp.text or 'login' in resp.url:
        print('⚠️ 登录失败：账号或密码错误，或系统结构变更')
        course_map = {i: [] for i in range(7)}
    else:
        print("✅ 登录成功，正在获取课表")
        week = get_current_week(SEMESTER_START)

        def get_semester_id(session):
            print("🧭 尝试从课程表页面直接获取 semester.id...")
    
            try:
        # 请求课程表页面
               course_table_url = 'https://jwxt.bjwlxy.cn/eams/courseTableForStd.action'
               response = session.get(course_table_url, timeout=10)
               response.raise_for_status()
        
        # 从 Set-Cookie 头中提取 semester.id
               semester_id = None
               if 'Set-Cookie' in response.headers:
                    cookies = response.headers['Set-Cookie'].split(';')
                    for cookie in cookies:
                       if 'courseTableForStdsemester.id' in cookie:
                          match = re.search(r'courseTableForStdsemester\.id=(\d+)', cookie)
                          if match:
                            semester_id = match.group(1)
                            print(f"✅ 从 Set-Cookie 头中获取到 semester.id: {semester_id}")
                            return semester_id
        
        # 如果从 Cookie 中未找到，尝试从 HTML 中提取
               print("⚠️ 未从 Set-Cookie 头中找到 semester.id，尝试从页面HTML中解析...")
               soup = BeautifulSoup(response.text, 'html.parser')
        
        # 尝试从下拉菜单中获取
               semester_select = soup.find('select', id='semester')
               if semester_select:
                  selected_option = semester_select.find('option', selected=True)
                  if selected_option:
                    semester_id = selected_option['value']
                    print(f"✅ 从页面下拉菜单中获取到 semester.id: {semester_id}")
                    return semester_id
        
        # 尝试从隐藏字段中获取
               semester_input = soup.find('input', {'name': 'semester.id'})
               if semester_input:
                  semester_id = semester_input.get('value')
                  if semester_id:
                   print(f"✅ 从页面隐藏字段中获取到 semester.id: {semester_id}")
                  return semester_id
        
        # 尝试从 JavaScript 变量中获取
               script_match = re.search(r'var\s+semesterId\s*=\s*["\']?(\d+)["\']?', response.text)
               if script_match:
                  semester_id = script_match.group(1)
                  print(f"✅ 从 JavaScript 变量中获取到 semester.id: {semester_id}")
                  return semester_id
        
        # 所有方法都失败
               raise RuntimeError("❌ 无法获取 semester.id：Set-Cookie、HTML和JS中均未找到")
        
            except Exception as e:
             print(f"❌ 获取 semester.id 出错：{e}")
             raise

        # 在获取学生ID之前调用这个函数
        week = get_current_week(SEMESTER_START)
        print(f"🧭 当前为第 {week} 周")

        # 获取 semester.id
        semester_id = get_semester_id(session)

        # 获取 ids (保持原有逻辑)
        # 修改获取 ids 的代码
        try:
                print("尝试获取学生 ID...")
                ids_resp = session.get('https://jwxt.bjwlxy.cn/eams/courseTableForStd!index.action', timeout=10)
                ids_resp.raise_for_status()
    
    # 尝试多种匹配模式
                ids_match = re.search(r'bg\.form\.addInput\(form,"ids","(\d+)"\);', ids_resp.text)
                if not ids_match:
                 ids_match = re.search(r'var\s+ids\s*=\s*"(\d+)"', ids_resp.text)
                if not ids_match:
                 ids_match = re.search(r'id=["\']ids["\']\s+value=["\'](\d+)["\']', ids_resp.text)
    
                if not ids_match:
                   print("❌ 所有匹配模式都未能找到学生ID")
                   print("📄 页面URL:", ids_resp.url)
                   print("📄 页面标题:", BeautifulSoup(ids_resp.text, 'html.parser').title.string)
                   raise RuntimeError("无法获取学生ID")
    
                student_ids = ids_match.group(1)
                print(f"✅ 获取学生ID成功: {student_ids}")
        except Exception as e:
               print(f"❌ 获取学生ID出错: {e}")
               raise
        course_url = 'https://jwxt.bjwlxy.cn/eams/courseTableForStd!courseTable.action'
        post_data = {
            'ignoreHead': '1',
            'setting.kind': 'std',
            'startWeek': str(week),
            'semester.id': '91',
            'ids': '31203'
        }
        course_headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://jwxt.bjwlxy.cn/eams/courseTableForStd!innerIndex.action',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://jwxt.bjwlxy.cn',
            'X-Requested-With': 'XMLHttpRequest'
        }
        try:
            resp = session.post(course_url, data=post_data, headers=course_headers, timeout=10)
            from datetime import datetime as dt

            def parse_course_from_js(js_text):
                course_map = {i: [] for i in range(7)}
                pattern = re.compile(
                    r'activity\s*=\s*new TaskActivity\((.*?)\);.*?index\s*=\s*(\d+)\*unitCount\+(\d+);',
                    re.DOTALL
                )
                for match in pattern.finditer(js_text):
                    args_str, day_num, section_num = match.groups()
                    args = [arg.strip().strip('"') for arg in re.split(r',(?![^()]*\))', args_str)]
                    if len(args) < 6:
                        continue
                    teacher = args[1].replace("actTeacherName.join(',')", "未知老师")
                    course_name = args[3]
                    place = args[5]
                    day = int(day_num)
                    section = int(section_num)
                    section_map = {
                        0: '1-2', 1: '1-2',
                        2: '3-4', 3: '3-4',
                        4: '5-6', 5: '5-6',
                        6: '7-8', 7: '7-8',
                        8: '9-10', 9: '9-10',
                    }
                    section_key = section_map.get(section, '')
                    time = period_time_map.get(section_key, '')
                    info = f"{course_name}（{teacher}）{place} 🕒 {time}"
                    course_map[day].append(info)

                for day in course_map:
                    def extract_time(line):
                        match = re.search(r'🕒 (\d{2}:\d{2})', line)
                        return dt.strptime(match.group(1), '%H:%M') if match else dt.strptime('23:59', '%H:%M')
                    course_map[day].sort(key=extract_time)
                return course_map

            course_map = parse_course_from_js(resp.text)

        except Exception as e:
            print(f"❌ 获取课表失败：{e}")
            course_map = {i: [] for i in range(7)}

def get_today_courses(course_map):
    today_index = datetime.now().weekday()
    return course_map.get(today_index, [])


def get_love_words():
    urls = [
        
        "https://api.lovelive.tools/api/SweetNothings",
        
        "https://api.vvhan.com/api/love?type=json",
        
        "https://api.1314.cool/words/api.php"
    ]

    random.shuffle(urls)

    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                # 判断响应内容类型
                if res.headers.get("Content-Type", "").startswith("application/json"):
                    data = res.json()
                    if "content" in data:
                        return data["content"]
                else:
                    return res.text.strip()
        except Exception as e:
            continue  # 失败自动尝试下一个

    # 全部失败时的备用情话
    return "💌 就算全世界都下雨，我也会来接你。"
def get_weather_tianapi():
    city = '宝鸡'
    url = f"http://api.tianapi.com/tianqi/index?key={TX_APIKEY}&city={city}"

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        if data["code"] == 200:
            weather_info = data["newslist"][0]
            wea = weather_info["weather"]
            low = weather_info["lowest"]
            high = weather_info["highest"]
            tips = weather_info["tips"]
            return f"🌦️ 宝鸡天气：{wea} {low}~{high}\n\n👕 穿衣建议：{tips}"
        else:
            return f"⚠️ 天气请求失败：{data['msg']}"
    except Exception as e:
        return f"⚠️ 天气请求异常：{e}"





def push_to_wechat(title, content_md, token, use_group=False, topic=None):
    if not ENABLE_PUSHPLUS or not token:
        print("📪 PushPlus 未启用或未配置 Token")
        return
    url = "https://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": title,
        "content": content_md,
        "template": "markdown"
    }
    if use_group and topic:
        data["topic"] = topic
    try:
        res = requests.post(url, json=data, timeout=10)
        if res.status_code == 200:
            print("✅ 推送成功 (PushPlus)")
        else:
            print("❌ 推送失败 (PushPlus)")
    except Exception as e:
        print(f"❌ 推送请求异常：{e}")


def push_to_bark(title, content):
    if not ENABLE_BARK or not BARK_URL:
        print("📪 Bark 未启用或未配置 URL")
        return
    try:
        res = requests.get(BARK_URL + f"{title}/{content}?isArchive=1", timeout=5)
        if res.status_code == 200:
            print("✅ 推送成功 (Bark)")
        else:
            print("❌ 推送失败 (Bark)")
    except Exception as e:
        print(f"❌ Bark 推送异常：{e}")
      
week = get_current_week(SEMESTER_START)
today_courses = get_today_courses(course_map)
today_str = datetime.now().strftime('%Y-%m-%d %A')
weather_info = get_weather_tianapi()
quote = quote = get_love_words()
()
send_time = datetime.now().strftime('%H:%M:%S')


msg = f"{weather_info}\n\n📅 **{today_str}**\n\n🧭 **第 {week} 周 · 今日课程：**\n\n"
if today_courses:
    msg += "| 课程名 | 上课地点 | 时间 |\n"
    msg += "|--------|----------|------|\n"
    pattern = r'(.+?)\(\d{6,}(?:\.\w+)?\)[（(](.+?)[）)](.+?) 🕒 (.+)'

    for line in today_courses:
        line = line.strip()
        print(f"DEBUG: 原始课程行: {repr(line)}")
        match = re.search(pattern, line)
        if match:
          name, teacher, place, time = match.groups()
          msg += f"| {name.strip()} | {place.strip()} | 🕒 {time.strip()} |\n"
        else:
          print(f"❌ 未匹配课程: {line}")
          msg += f"| {line} | - | - |\n"

else:
    msg += "🎉 今天没有课或登录失败"



msg += f"\n\n🍵 **每日一言**：_{quote}_\n\n🕓 **推送时间**：{send_time}\n\n**Leisure💗Tiffany**"

with open('今日课表.md', 'w', encoding='utf-8') as f:
    f.write(msg)

push_to_wechat("📚 今日课表", msg, PUSHPLUS_TOKEN, use_group=USE_GROUP_PUSH, topic=GROUP_TOPIC)
push_to_bark("📚 今日课表", msg)
