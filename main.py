import os
import re
import requests
import tkinter as tk
from tkinter import messagebox

# ================= 1. 核心配置区 =================
MOODLE_BASE_URL = "https://l.xmu.edu.my"
API_URL = f"{MOODLE_BASE_URL}/webservice/rest/server.php"
# 请使用者在这里填入你的本地下载路径（例如 Windows: r"D:\Moodle_Sync"）
BASE_DOWNLOAD_DIR = r"请替换为你的路径"

COURSE_FOLDER_MAP = {
     # 请使用者自行查阅 Moodle 课程 ID，并在这里建立映射
     COURSE_FOLDER_MAP = {
     # 示例: 13003: "arm_course",
 }
}



# ================= 2. 可视化登录模块 (V1.2 新增) =================
def get_moodle_token_gui():
    """弹出一个 UI 窗口，让用户输入账号密码，自动换取 Token"""
    token_result = None

    def attempt_login():
        nonlocal token_result
        username = entry_user.get()
        password = entry_pass.get()

        if not username or not password:
            messagebox.showwarning("警告", "账号和密码不能为空！")
            return

        login_btn.config(text="登录中...", state=tk.DISABLED)
        root.update()

        login_url = f"{MOODLE_BASE_URL}/login/token.php"
        params = {
            "username": username,
            "password": password,
            "service": "moodle_mobile_app"
        }

        try:
            response = requests.get(login_url, params=params, timeout=10).json()
            if 'token' in response:
                token_result = response['token']
                messagebox.showinfo("成功", "✅ 登录成功！即将开始下载文件。")
                root.destroy()  # 关闭 UI 窗口，继续执行主程序
            else:
                messagebox.showerror("失败", "❌ 账号或密码错误，请重试！")
                login_btn.config(text="登 录", state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("网络错误", f"无法连接到学校服务器: {e}")
            login_btn.config(text="登 录", state=tk.NORMAL)

    # 绘制 UI 界面
    root = tk.Tk()
    root.title("XMUM 课件自动下载引擎 V1.2")
    root.geometry("350x200")

    # 将窗口居中显示在屏幕上
    root.eval('tk::PlaceWindow . center')

    tk.Label(root, text="Moodle 学号:").pack(pady=(15, 0))
    entry_user = tk.Entry(root, width=30)
    entry_user.pack()

    tk.Label(root, text="Moodle 密码:").pack(pady=(10, 0))
    entry_pass = tk.Entry(root, width=30, show="*")  # show="*" 用来隐藏密码输入
    entry_pass.pack()

    # 绑定回车键快捷登录
    root.bind('<Return>', lambda event: attempt_login())

    login_btn = tk.Button(root, text="登 录", width=15, command=attempt_login, bg="#4CAF50", fg="white")
    login_btn.pack(pady=20)

    root.mainloop()  # 阻塞程序，直到窗口关闭
    return token_result


# ================= 3. 工具模块 =================
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name)


def call_moodle_api(token, wsfunction, **kwargs):
    params = {"wstoken": token, "wsfunction": wsfunction, "moodlewsrestformat": "json"}
    params.update(kwargs)
    response = requests.get(API_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


# ================= 4. 主干引擎 =================
if __name__ == "__main__":
    print(">>> 启动 V1.2 带 UI 归档引擎...")

    # 步骤 A：呼叫 UI 获取 Token (绝不把密码写死在代码里！)
    MY_TOKEN = get_moodle_token_gui()

    if not MY_TOKEN:
        print("❌ 登录被取消或失败，程序终止。")
        exit()

    print(f"✅ 成功获取临时通行证: {MY_TOKEN[:5]}***")

    # 步骤 B：获取用户信息和课程列表
    site_info = call_moodle_api(MY_TOKEN, "core_webservice_get_site_info")
    courses = call_moodle_api(MY_TOKEN, "core_enrol_get_users_courses", userid=site_info['userid'])

    # 步骤 C：执行核心下载与分类路由
    for course in courses:
        course_id = course.get('id')
        if course_id not in COURSE_FOLDER_MAP:
            continue

        custom_folder_name = COURSE_FOLDER_MAP[course_id]
        course_folder_path = os.path.join(BASE_DOWNLOAD_DIR, custom_folder_name)
        os.makedirs(course_folder_path, exist_ok=True)

        print(f"\n📂 正在同步: [{custom_folder_name}]")

        sections = call_moodle_api(MY_TOKEN, "core_course_get_contents", courseid=course_id)
        if isinstance(sections, dict) and 'exception' in sections:
            continue

        for section in sections:
            for module in section.get('modules', []):
                if module.get('modname') in ['resource', 'folder']:
                    for content in module.get('contents', []):
                        if content.get('type') == 'file':
                            filename = content.get('filename')
                            download_url = f"{content.get('fileurl')}&token={MY_TOKEN}"

                            safe_filename = sanitize_filename(filename)
                            file_save_path = os.path.join(course_folder_path, safe_filename)

                            if os.path.exists(file_save_path):
                                print(f"   ⏩ 已存在，跳过: {safe_filename}")
                                continue

                            print(f"   ⬇️ 下载中: {safe_filename} ...", end="", flush=True)

                            try:
                                file_response = requests.get(download_url, timeout=30)
                                file_response.raise_for_status()
                                with open(file_save_path, 'wb') as f:
                                    f.write(file_response.content)
                                print(" [成功]")
                            except Exception as e:
                                print(f" [失败: {e}]")

    print("\n🎉 V1.2 归档完成！你的课件已全部就绪。")