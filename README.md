# xmum-moodle-file-downloader
an automatic downloader for file in moodle
# XMUM Moodle-DL 

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

针对厦门大学马来西亚分校 (XMUM) 学生的 Moodle 课件自动下载归档引擎。

##  功能特性
- **UI 交互登录**：无需手动抓取 Token，直接通过学号密码登录，安全便捷。
- **精准路由分类**：自动将不同课程的文件（PDF/PPT）归档至指定的文件夹。
- **增量同步**：智能识别已下载文件，跳过重复内容，节省流量与时间。
- **文件名净化**：自动处理 Windows 不合规字符，防止下载中断。
## 本工具采用 “ID-文件夹”映射机制，支持用户高度定制化归档路径。
你可以通过修改 main.py 中的 COURSE_FOLDER_MAP 字典，将晦涩的 Moodle 课程编号映射为清爽的本地文件夹名：
-**instance：**
13003 (ARM 汇编) ➔ /arm/
12825 (计算机网络) ➔ /network/
系统会自动完成 Windows 非法字符过滤，确保路径创建万无一失。

##  免责声明
本工具仅用于学习交流，学生小白制作，制作粗糙简略，欢迎学习交流，请遵守 XMUM 网络使用规定。切勿用于商业用途或恶意大规模爬取服务器资源。
