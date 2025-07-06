import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
import os
from PIL import Image, ImageTk
import qrcode
import io

class BilibiliDownloaderClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("清风.exe")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        self.root.resizable(True, True)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass
        
        # 当前页面状态
        self.current_page = "search"
        
        # 下载任务列表
        self.download_tasks = []
        
        # 创建主界面
        self.create_main_interface()
        
    def create_main_interface(self):
        """创建主界面"""
        # 左侧导航栏
        self.create_sidebar()
        
        # 主内容区域
        self.main_frame = tk.Frame(self.root, bg='#2b2b2b')
        self.main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 默认显示搜索页面
        self.show_search_page()
        
    def create_sidebar(self):
        """创建左侧导航栏"""
        sidebar = tk.Frame(self.root, bg='#1e1e1e', width=60)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # 应用图标
        icon_frame = tk.Frame(sidebar, bg='#1e1e1e', height=60)
        icon_frame.pack(fill=tk.X, pady=10)
        
        # 创建一个简单的图标 - 使用B站风格的图标
        icon_canvas = tk.Canvas(icon_frame, width=40, height=40, bg='#1e1e1e', highlightthickness=0)
        icon_canvas.pack()
        
        # 绘制简单的B站风格图标
        icon_canvas.create_oval(5, 5, 35, 35, fill='#00a1d6', outline='')
        icon_canvas.create_text(20, 20, text='B', fill='white', font=('Arial', 16, 'bold'))
        
        # 搜索按钮
        search_btn = self.create_nav_button(sidebar, "🔍", self.show_search_page, active=(self.current_page == "search"))
        search_btn.pack(pady=10)
        
        # 下载按钮
        download_btn = self.create_nav_button(sidebar, "⬇", self.show_download_page, active=(self.current_page == "download"))
        download_btn.pack(pady=10)
        
        # 底部设置按钮
        settings_frame = tk.Frame(sidebar, bg='#1e1e1e')
        settings_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        settings_btn = self.create_nav_button(settings_frame, "⚙", self.show_settings_page, active=(self.current_page == "settings"))
        settings_btn.pack(pady=5)
        
        about_btn = self.create_nav_button(settings_frame, "ℹ", self.show_about)
        about_btn.pack(pady=5)
        
    def create_nav_button(self, parent, text, command, active=False):
        """创建导航按钮"""
        bg_color = '#0078d4' if active else '#1e1e1e'
        btn = tk.Button(parent, text=text, bg=bg_color, fg='white', 
                       font=('Arial', 16), border=0, width=3, height=2,
                       command=command, cursor='hand2')
        
        # 添加悬停效果
        def on_enter(e):
            if not active:
                btn.configure(bg='#404040')
        
        def on_leave(e):
            if not active:
                btn.configure(bg='#1e1e1e')
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
        
    def clear_main_frame(self):
        """清空主内容区域"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    def show_search_page(self):
        """显示搜索页面"""
        self.current_page = "search"
        self.clear_main_frame()
        self.create_sidebar()  # 重新创建侧边栏以更新按钮状态
        
        # 搜索框区域
        search_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        search_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 搜索容器
        search_container = tk.Frame(search_frame, bg='#404040', relief=tk.FLAT)
        search_container.pack(fill=tk.X)
        
        # 搜索输入框
        self.search_entry = tk.Entry(search_container, bg='#404040', fg='white', 
                                    font=('Arial', 12), relief=tk.FLAT, border=0)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        self.search_entry.insert(0, "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...")
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        self.search_entry.bind('<Return>', self.perform_search)
        
        # 按钮容器
        button_container = tk.Frame(search_container, bg='#404040')
        button_container.pack(side=tk.RIGHT, padx=5)
        
        # 自动检测按钮
        auto_detect_btn = tk.Button(button_container, text="自动检测", bg='#0078d4', fg='white', 
                                   font=('Arial', 10), relief=tk.FLAT, command=self.auto_detect,
                                   cursor='hand2', padx=15, pady=5)
        auto_detect_btn.pack(side=tk.RIGHT, padx=2)
        
        # 搜索按钮
        search_btn = tk.Button(button_container, text="🔍", bg='#404040', fg='white', 
                              font=('Arial', 12), relief=tk.FLAT, command=self.perform_search,
                              cursor='hand2', width=3)
        search_btn.pack(side=tk.RIGHT, padx=2)
        
        # 空状态显示
        self.show_empty_state()
        
    def show_download_page(self):
        """显示下载页面"""
        self.current_page = "download"
        self.clear_main_frame()
        self.create_sidebar()  # 重新创建侧边栏以更新按钮状态
        
        # 顶部标签栏
        tab_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        tab_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        
        # 标签按钮
        self.create_tab_button(tab_frame, "等待中", False).pack(side=tk.LEFT, padx=(0, 20))
        self.create_tab_button(tab_frame, "进行中", False).pack(side=tk.LEFT, padx=(0, 20))
        self.create_tab_button(tab_frame, "已完成", True).pack(side=tk.LEFT)
        
        # 下载列表区域
        if self.download_tasks:
            self.show_download_list()
        else:
            self.show_empty_download_state()
            
    def create_tab_button(self, parent, text, active=False):
        """创建标签按钮"""
        color = '#0078d4' if active else '#888'
        btn = tk.Button(parent, text=text, bg='#2b2b2b', fg=color, 
                       font=('Arial', 12), relief=tk.FLAT, border=0, cursor='hand2')
        return btn
        
    def show_settings_page(self):
        """显示设置页面"""
        self.current_page = "settings"
        self.clear_main_frame()
        self.create_sidebar()  # 重新创建侧边栏以更新按钮状态
        
        # 创建滚动区域
        canvas = tk.Canvas(self.main_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # 设置标题
        title_frame = tk.Frame(scrollable_frame, bg='#2b2b2b')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        settings_icon = tk.Label(title_frame, text="⚙", bg='#2b2b2b', fg='white', font=('Arial', 16))
        settings_icon.pack(side=tk.LEFT)
        
        settings_title = tk.Label(title_frame, text="设置", bg='#2b2b2b', fg='white', font=('Arial', 16, 'bold'))
        settings_title.pack(side=tk.LEFT, padx=(10, 0))
        
        help_btn = tk.Button(title_frame, text="?", bg='#2b2b2b', fg='#888', 
                            font=('Arial', 12), relief=tk.FLAT, border=0, cursor='hand2')
        help_btn.pack(side=tk.RIGHT)
        
        # 保存路径设置
        self.create_settings_section(scrollable_frame, "📁", "保存路径", "存储")
        
        # 输出文件路径
        output_frame = tk.Frame(scrollable_frame, bg='#2b2b2b')
        output_frame.pack(fill=tk.X, pady=5)
        
        output_label = tk.Label(output_frame, text="输出文件", bg='#2b2b2b', fg='white', font=('Arial', 10))
        output_label.pack(anchor=tk.W)
        
        path_container = tk.Frame(output_frame, bg='#2b2b2b')
        path_container.pack(fill=tk.X, pady=5)
        
        self.output_path = tk.Entry(path_container, bg='#404040', fg='white', 
                                   font=('Arial', 10), relief=tk.FLAT, border=0)
        self.output_path.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 5))
        self.output_path.insert(0, "C:\\Users\\hhhjh\\Desktop")
        
        browse_btn = tk.Button(path_container, text="📁", bg='#0078d4', fg='white', 
                              font=('Arial', 10), relief=tk.FLAT, command=self.browse_folder,
                              cursor='hand2', padx=10)
        browse_btn.pack(side=tk.RIGHT, padx=2)
        
        download_btn = tk.Button(path_container, text="下载", bg='#404040', fg='white', 
                                font=('Arial', 10), relief=tk.FLAT, cursor='hand2', padx=10)
        download_btn.pack(side=tk.RIGHT, padx=2)
        
        # 临时文件路径
        temp_frame = tk.Frame(scrollable_frame, bg='#2b2b2b')
        temp_frame.pack(fill=tk.X, pady=15)
        
        temp_label = tk.Label(temp_frame, text="临时文件", bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        temp_label.pack(anchor=tk.W)
        
        temp_desc = tk.Label(temp_frame, text="应用首先下载至此文件夹，随后会处理转移至输出文件夹。", 
                            bg='#2b2b2b', fg='#888', font=('Arial', 9))
        temp_desc.pack(anchor=tk.W, pady=(2, 5))
        
        temp_path_container = tk.Frame(temp_frame, bg='#2b2b2b')
        temp_path_container.pack(fill=tk.X)
        
        self.temp_path = tk.Entry(temp_path_container, bg='#404040', fg='white', 
                                 font=('Arial', 10), relief=tk.FLAT, border=0)
        self.temp_path.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 5))
        self.temp_path.insert(0, "C:\\Users\\hhhjh\\AppData\\Local\\Temp\\")
        
        temp_browse_btn = tk.Button(temp_path_container, text="📁", bg='#0078d4', fg='white', 
                                   font=('Arial', 10), relief=tk.FLAT, command=self.browse_temp_folder,
                                   cursor='hand2', padx=10)
        temp_browse_btn.pack(side=tk.RIGHT)
        
        # 缓存设置
        cache_frame = tk.Frame(scrollable_frame, bg='#2b2b2b')
        cache_frame.pack(fill=tk.X, pady=20)
        
        cache_header = tk.Frame(cache_frame, bg='#2b2b2b')
        cache_header.pack(fill=tk.X)
        
        cache_icon = tk.Label(cache_header, text="💾", bg='#2b2b2b', fg='white', font=('Arial', 12))
        cache_icon.pack(side=tk.LEFT)
        
        cache_label = tk.Label(cache_header, text="缓存", bg='#2b2b2b', fg='white', font=('Arial', 12, 'bold'))
        cache_label.pack(side=tk.LEFT, padx=(10, 0))
        
        cache_desc = tk.Label(cache_frame, text="用户数据缓存有每条信息，下载记录等重要数据，切勿随意删除。", 
                             bg='#2b2b2b', fg='#888', font=('Arial', 9))
        cache_desc.pack(anchor=tk.W, pady=(5, 10))
        
        # 缓存项目
        cache_items = [
            ("日志", "23.62 KB"),
            ("临时文件", "0.00 KB"),
            ("Webview", "38.53 MB"),
            ("用户数据库", "28.00 KB")
        ]
        
        for item_name, item_size in cache_items:
            self.create_cache_item(cache_frame, item_name, item_size)
        
        # 语言设置
        lang_frame = tk.Frame(scrollable_frame, bg='#2b2b2b')
        lang_frame.pack(fill=tk.X, pady=20)
        
        lang_header = tk.Frame(lang_frame, bg='#2b2b2b')
        lang_header.pack(fill=tk.X)
        
        lang_icon = tk.Label(lang_header, text="🌐", bg='#2b2b2b', fg='white', font=('Arial', 12))
        lang_icon.pack(side=tk.LEFT)
        
        lang_label = tk.Label(lang_header, text="语言", bg='#2b2b2b', fg='white', font=('Arial', 12, 'bold'))
        lang_label.pack(side=tk.LEFT, padx=(10, 0))
        
        lang_container = tk.Frame(lang_frame, bg='#2b2b2b')
        lang_container.pack(fill=tk.X, pady=5)
        
        lang_var = tk.StringVar(value="简体中文 cn")
        lang_combo = ttk.Combobox(lang_container, textvariable=lang_var, state="readonly", 
                                 values=["简体中文 cn", "English en"], width=20)
        lang_combo.pack(side=tk.RIGHT)
        
    def create_settings_section(self, parent, icon, title, button_text):
        """创建设置区块"""
        section_frame = tk.Frame(parent, bg='#2b2b2b')
        section_frame.pack(fill=tk.X, pady=10)
        
        header_frame = tk.Frame(section_frame, bg='#2b2b2b')
        header_frame.pack(fill=tk.X)
        
        icon_label = tk.Label(header_frame, text=icon, bg='#2b2b2b', fg='white', font=('Arial', 12))
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame, text=title, bg='#2b2b2b', fg='white', font=('Arial', 12, 'bold'))
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        if button_text:
            button = tk.Button(header_frame, text=button_text, bg='#404040', fg='white', 
                              font=('Arial', 10), relief=tk.FLAT, cursor='hand2', padx=15)
            button.pack(side=tk.RIGHT)
        
        return section_frame
        
    def create_cache_item(self, parent, name, size):
        """创建缓存项目"""
        item_frame = tk.Frame(parent, bg='#2b2b2b')
        item_frame.pack(fill=tk.X, pady=2)
        
        name_label = tk.Label(item_frame, text=name, bg='#2b2b2b', fg='white', font=('Arial', 10))
        name_label.pack(side=tk.LEFT)
        
        clean_btn = tk.Button(item_frame, text="🗑", bg='#0078d4', fg='white', 
                             font=('Arial', 10), relief=tk.FLAT, cursor='hand2', padx=8)
        clean_btn.pack(side=tk.RIGHT)
        
        size_label = tk.Label(item_frame, text=size, bg='#2b2b2b', fg='#888', font=('Arial', 10))
        size_label.pack(side=tk.RIGHT, padx=(0, 10))
        
    def generate_qr_code(self, data="https://www.bilibili.com/"):
        """生成二维码"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 转换为tkinter可用的格式
            photo = ImageTk.PhotoImage(img)
            return photo
        except:
            return None
        
    def show_login_page(self):
        """显示登录页面"""
        login_window = tk.Toplevel(self.root)
        login_window.title("登录")
        login_window.geometry("900x650")
        login_window.configure(bg='#2b2b2b')
        login_window.transient(self.root)
        login_window.grab_set()
        login_window.resizable(False, False)
        
        # 居中显示
        login_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 75))
        
        main_container = tk.Frame(login_window, bg='#2b2b2b')
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # 左侧二维码区域
        left_frame = tk.Frame(main_container, bg='#2b2b2b')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 40))
        
        qr_title = tk.Label(left_frame, text="扫描二维码登录", bg='#2b2b2b', fg='white', 
                           font=('Arial', 16, 'bold'))
        qr_title.pack(pady=(0, 20))
        
        # 二维码区域
        qr_container = tk.Frame(left_frame, bg='white', relief=tk.RAISED, bd=2)
        qr_container.pack(pady=20)
        
        # 尝试生成真实的二维码
        qr_photo = self.generate_qr_code()
        if qr_photo:
            qr_label = tk.Label(qr_container, image=qr_photo, bg='white')
            qr_label.image = qr_photo  # 保持引用
        else:
            # 备用方案：文本占位符
            qr_label = tk.Label(qr_container, text="QR Code\nPlaceholder", bg='white', fg='black', 
                               font=('Arial', 12), width=20, height=10)
        qr_label.pack(padx=10, pady=10)
        
        # 二维码说明
        qr_desc_frame = tk.Frame(left_frame, bg='#2b2b2b')
        qr_desc_frame.pack(pady=10)
        
        qr_desc1 = tk.Label(qr_desc_frame, text="请使用 ", bg='#2b2b2b', fg='#888', font=('Arial', 10))
        qr_desc1.pack(side=tk.LEFT)
        
        qr_desc2 = tk.Label(qr_desc_frame, text="哔哩哔哩客户端", bg='#2b2b2b', fg='#00a1d6', 
                           font=('Arial', 10, 'underline'), cursor='hand2')
        qr_desc2.pack(side=tk.LEFT)
        
        qr_desc3 = tk.Label(qr_desc_frame, text=" 扫码登录", bg='#2b2b2b', fg='#888', font=('Arial', 10))
        qr_desc3.pack(side=tk.LEFT)
        
        qr_desc4 = tk.Label(left_frame, text="或点击下载APP", bg='#2b2b2b', fg='#888', font=('Arial', 10))
        qr_desc4.pack()
        
        # 底部卡通形象
        char_frame = tk.Frame(left_frame, bg='#2b2b2b')
        char_frame.pack(side=tk.BOTTOM, pady=20)
        
        char_canvas = tk.Canvas(char_frame, width=80, height=80, bg='#2b2b2b', highlightthickness=0)
        char_canvas.pack()
        
        # 绘制简单的卡通形象
        char_canvas.create_oval(20, 20, 60, 60, fill='#00a1d6', outline='')
        char_canvas.create_oval(30, 30, 35, 35, fill='white', outline='')
        char_canvas.create_oval(45, 30, 50, 35, fill='white', outline='')
        char_canvas.create_arc(25, 35, 55, 55, start=0, extent=180, fill='white', outline='')
        
        # 右侧登录表单区域
        right_frame = tk.Frame(main_container, bg='#2b2b2b')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 登录方式选择
        login_tabs = tk.Frame(right_frame, bg='#2b2b2b')
        login_tabs.pack(fill=tk.X, pady=(0, 30))
        
        self.login_mode = tk.StringVar(value="password")
        
        pwd_tab = tk.Radiobutton(login_tabs, text="密码登录", variable=self.login_mode, value="password",
                                bg='#2b2b2b', fg='#00a1d6', font=('Arial', 12), 
                                selectcolor='#2b2b2b', activebackground='#2b2b2b',
                                command=self.switch_login_mode)
        pwd_tab.pack(side=tk.LEFT, padx=(0, 20))
        
        sms_tab = tk.Radiobutton(login_tabs, text="短信登录", variable=self.login_mode, value="sms",
                                bg='#2b2b2b', fg='#888', font=('Arial', 12),
                                selectcolor='#2b2b2b', activebackground='#2b2b2b',
                                command=self.switch_login_mode)
        sms_tab.pack(side=tk.LEFT)
        
        # 登录表单容器
        self.form_container = tk.Frame(right_frame, bg='#2b2b2b')
        self.form_container.pack(fill=tk.X, pady=20)
        
        # 创建密码登录表单
        self.create_password_form()
        
        # 协议说明
        agreement_frame = tk.Frame(right_frame, bg='#2b2b2b')
        agreement_frame.pack(side=tk.BOTTOM, pady=20)
        
        agreement_text = "该应用产生与收集的所有数据仅存储于用户本地\n登录即代表同意"
        agreement_label = tk.Label(agreement_frame, text=agreement_text, bg='#2b2b2b', fg='#888', 
                                  font=('Arial', 9), justify=tk.CENTER)
        agreement_label.pack(pady=10)
        
        # 协议链接
        links_frame = tk.Frame(agreement_frame, bg='#2b2b2b')
        links_frame.pack()
        
        privacy_link = tk.Label(links_frame, text="隐私政策", bg='#2b2b2b', fg='#00a1d6', 
                               font=('Arial', 9, 'underline'), cursor="hand2")
        privacy_link.pack(side=tk.LEFT)
        
        and_label = tk.Label(links_frame, text=" 和 ", bg='#2b2b2b', fg='#888', font=('Arial', 9))
        and_label.pack(side=tk.LEFT)
        
        terms_link = tk.Label(links_frame, text="用户协议", bg='#2b2b2b', fg='#00a1d6', 
                             font=('Arial', 9, 'underline'), cursor="hand2")
        terms_link.pack(side=tk.LEFT)
        
        # 底部卡通形象
        char_frame2 = tk.Frame(right_frame, bg='#2b2b2b')
        char_frame2.pack(side=tk.BOTTOM, anchor=tk.E, padx=20)
        
        char_canvas2 = tk.Canvas(char_frame2, width=60, height=60, bg='#2b2b2b', highlightthickness=0)
        char_canvas2.pack()
        
        # 绘制另一个卡通形象
        char_canvas2.create_oval(10, 10, 50, 50, fill='#ff6b9d', outline='')
        char_canvas2.create_oval(20, 20, 25, 25, fill='white', outline='')
        char_canvas2.create_oval(35, 20, 40, 25, fill='white', outline='')
        char_canvas2.create_arc(15, 25, 45, 45, start=0, extent=180, fill='white', outline='')
        
        # 保存登录窗口引用
        self.login_window = login_window
        
    def create_password_form(self):
        """创建密码登录表单"""
        # 清空表单容器
        for widget in self.form_container.winfo_children():
            widget.destroy()
            
        # 账号输入
        account_label = tk.Label(self.form_container, text="账号", bg='#2b2b2b', fg='white', font=('Arial', 12))
        account_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.account_entry = tk.Entry(self.form_container, bg='#404040', fg='white', 
                                     font=('Arial', 12), relief=tk.FLAT, border=0)
        self.account_entry.pack(fill=tk.X, ipady=12, pady=(0, 15))
        self.account_entry.insert(0, "请输入账号")
        self.account_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(self.account_entry, "请输入账号"))
        self.account_entry.bind('<FocusOut>', lambda e: self.restore_placeholder(self.account_entry, "请输入账号"))
        
        # 密码输入
        password_label = tk.Label(self.form_container, text="密码", bg='#2b2b2b', fg='white', font=('Arial', 12))
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = tk.Entry(self.form_container, bg='#404040', fg='white', 
                                      font=('Arial', 12), relief=tk.FLAT, border=0, show="*")
        self.password_entry.pack(fill=tk.X, ipady=12, pady=(0, 20))
        self.password_entry.insert(0, "请输入密码")
        self.password_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(self.password_entry, "请输入密码", True))
        self.password_entry.bind('<FocusOut>', lambda e: self.restore_placeholder(self.password_entry, "请输入密码", True))
        
        # 登录按钮
        login_btn = tk.Button(self.form_container, text="登录", bg='#00a1d6', fg='white', 
                             font=('Arial', 12, 'bold'), relief=tk.FLAT, command=self.perform_login,
                             cursor='hand2')
        login_btn.pack(fill=tk.X, pady=10, ipady=12)
        
    def create_sms_form(self):
        """创建短信登录表单"""
        # 清空表单容器
        for widget in self.form_container.winfo_children():
            widget.destroy()
            
        # 手机号输入
        phone_label = tk.Label(self.form_container, text="手机号", bg='#2b2b2b', fg='white', font=('Arial', 12))
        phone_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.phone_entry = tk.Entry(self.form_container, bg='#404040', fg='white', 
                                   font=('Arial', 12), relief=tk.FLAT, border=0)
        self.phone_entry.pack(fill=tk.X, ipady=12, pady=(0, 15))
        self.phone_entry.insert(0, "请输入手机号")
        self.phone_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(self.phone_entry, "请输入手机号"))
        self.phone_entry.bind('<FocusOut>', lambda e: self.restore_placeholder(self.phone_entry, "请输入手机号"))
        
        # 验证码输入
        code_frame = tk.Frame(self.form_container, bg='#2b2b2b')
        code_frame.pack(fill=tk.X, pady=(0, 20))
        
        code_label = tk.Label(code_frame, text="验证码", bg='#2b2b2b', fg='white', font=('Arial', 12))
        code_label.pack(anchor=tk.W, pady=(0, 5))
        
        code_input_frame = tk.Frame(code_frame, bg='#2b2b2b')
        code_input_frame.pack(fill=tk.X)
        
        self.code_entry = tk.Entry(code_input_frame, bg='#404040', fg='white', 
                                  font=('Arial', 12), relief=tk.FLAT, border=0)
        self.code_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)
        self.code_entry.insert(0, "请输入验证码")
        self.code_entry.bind('<FocusIn>', lambda e: self.clear_placeholder(self.code_entry, "请输入验证码"))
        self.code_entry.bind('<FocusOut>', lambda e: self.restore_placeholder(self.code_entry, "请输入验证码"))
        
        send_code_btn = tk.Button(code_input_frame, text="发送验证码", bg='#404040', fg='white', 
                                 font=('Arial', 10), relief=tk.FLAT, cursor='hand2', padx=15)
        send_code_btn.pack(side=tk.RIGHT, padx=(10, 0), ipady=12)
        
        # 登录按钮
        login_btn = tk.Button(self.form_container, text="登录", bg='#00a1d6', fg='white', 
                             font=('Arial', 12, 'bold'), relief=tk.FLAT, command=self.perform_sms_login,
                             cursor='hand2')
        login_btn.pack(fill=tk.X, pady=10, ipady=12)
        
    def switch_login_mode(self):
        """切换登录模式"""
        if self.login_mode.get() == "password":
            self.create_password_form()
        else:
            self.create_sms_form()
            
    def clear_placeholder(self, entry, placeholder, is_password=False):
        """清除占位符"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            if is_password:
                entry.config(show="*")
                
    def restore_placeholder(self, entry, placeholder, is_password=False):
        """恢复占位符"""
        if not entry.get():
            if is_password:
                entry.config(show="")
            entry.insert(0, placeholder)
            if is_password:
                entry.config(show="*")
        
    def show_empty_state(self):
        """显示空状态"""
        empty_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        empty_frame.pack(fill=tk.BOTH, expand=True)
        
        # 居中显示空状态
        center_frame = tk.Frame(empty_frame, bg='#2b2b2b')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 空状态图标
        icon_canvas = tk.Canvas(center_frame, width=100, height=100, bg='#2b2b2b', highlightthickness=0)
        icon_canvas.pack()
        
        # 绘制空状态图标
        icon_canvas.create_oval(25, 25, 75, 75, fill='#404040', outline='')
        icon_canvas.create_text(50, 50, text='📱', fill='white', font=('Arial', 30))
        
        empty_text = tk.Label(center_frame, text="此处列为空～", bg='#2b2b2b', fg='#666', 
                             font=('Arial', 14))
        empty_text.pack(pady=20)
        
    def show_empty_download_state(self):
        """显示下载页面空状态"""
        empty_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        empty_frame.pack(fill=tk.BOTH, expand=True)
        
        # 居中显示空状态
        center_frame = tk.Frame(empty_frame, bg='#2b2b2b')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 空状态图标
        icon_canvas = tk.Canvas(center_frame, width=100, height=100, bg='#2b2b2b', highlightthickness=0)
        icon_canvas.pack()
        
        # 绘制下载图标
        icon_canvas.create_oval(25, 25, 75, 75, fill='#404040', outline='')
        icon_canvas.create_text(50, 50, text='📥', fill='white', font=('Arial', 30))
        
        empty_text = tk.Label(center_frame, text="暂无下载任务", bg='#2b2b2b', fg='#666', 
                             font=('Arial', 14))
        empty_text.pack(pady=20)
        
    def show_download_list(self):
        """显示下载列表"""
        # 创建滚动区域
        canvas = tk.Canvas(self.main_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#2b2b2b')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # 示例下载任务
        self.create_download_task(scrollable_frame, 
                                 "【Dead Inside】【循环歌单】\"我点炸弹，书桌如心脏狂跳\"",
                                 "ufs8QchDG87sjZ20",
                                 "2025-06-28 09:39:01",
                                 100.0,
                                 "完成")
        
    def create_download_task(self, parent, title, task_id, time, progress, status):
        """创建下载任务项"""
        task_frame = tk.Frame(parent, bg='#333333', relief=tk.RAISED, bd=1)
        task_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 任务信息区域
        info_frame = tk.Frame(task_frame, bg='#333333')
        info_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # 标题和ID
        title_frame = tk.Frame(info_frame, bg='#333333')
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text=title, bg='#333333', fg='white', 
                              font=('Arial', 12), anchor=tk.W)
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        id_label = tk.Label(title_frame, text=task_id, bg='#333333', fg='#888', 
                           font=('Arial', 10))
        id_label.pack(side=tk.RIGHT)
        
        # 时间
        time_label = tk.Label(info_frame, text=time, bg='#333333', fg='#888', 
                             font=('Arial', 10), anchor=tk.W)
        time_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 进度区域
        progress_frame = tk.Frame(task_frame, bg='#333333')
        progress_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # 状态和进度条
        status_frame = tk.Frame(progress_frame, bg='#333333')
        status_frame.pack(fill=tk.X, pady=5)
        
        status_label = tk.Label(status_frame, text=status, bg='#333333', fg='white', 
                               font=('Arial', 10))
        status_label.pack(side=tk.LEFT)
        
        # 进度条容器
        progress_container = tk.Frame(status_frame, bg='#555555', height=6)
        progress_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        progress_container.pack_propagate(False)
        
        # 进度条
        progress_width = int(progress_container.winfo_reqwidth() * progress / 100) if progress > 0 else 200
        progress_bar = tk.Frame(progress_container, bg='#00a1d6', height=6)
        progress_bar.pack(side=tk.LEFT, fill=tk.Y)
        progress_bar.configure(width=progress_width)
        
        percent_label = tk.Label(status_frame, text=f"{progress:.1f} %", bg='#333333', fg='white', 
                                font=('Arial', 10))
        percent_label.pack(side=tk.RIGHT)
        
        # 操作按钮
        action_frame = tk.Frame(task_frame, bg='#333333')
        action_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # 按钮容器
        button_container = tk.Frame(action_frame, bg='#333333')
        button_container.pack(side=tk.RIGHT)
        
        # 操作按钮
        delete_btn = tk.Button(button_container, text="🗑", bg='#555555', fg='white', 
                              font=('Arial', 12), relief=tk.FLAT, cursor='hand2', width=3)
        delete_btn.pack(side=tk.RIGHT, padx=2)
        
        folder_btn = tk.Button(button_container, text="📁", bg='#555555', fg='white', 
                              font=('Arial', 12), relief=tk.FLAT, cursor='hand2', width=3)
        folder_btn.pack(side=tk.RIGHT, padx=2)
        
        pause_btn = tk.Button(button_container, text="⏸", bg='#555555', fg='white', 
                             font=('Arial', 12), relief=tk.FLAT, cursor='hand2', width=3)
        pause_btn.pack(side=tk.RIGHT, padx=2)
        
    def on_search_focus_in(self, event):
        """搜索框获得焦点时清空占位符"""
        if self.search_entry.get() == "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg='white')
            
    def on_search_focus_out(self, event):
        """搜索框失去焦点时恢复占位符"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...")
            self.search_entry.configure(fg='#888')
            
    def perform_search(self, event=None):
        """执行搜索"""
        query = self.search_entry.get().strip()
        if query and query != "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...":
            messagebox.showinfo("搜索", f"正在搜索: {query}")
            # 这里可以添加实际的搜索逻辑
            # 模拟添加下载任务
            self.download_tasks.append({
                'title': query,
                'id': f'task_{len(self.download_tasks)}',
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'progress': 0,
                'status': '等待中'
            })
            
    def auto_detect(self):
        """自动检测"""
        messagebox.showinfo("自动检测", "正在自动检测链接类型...")
        
    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.output_path.delete(0, tk.END)
            self.output_path.insert(0, folder)
            
    def browse_temp_folder(self):
        """浏览临时文件夹"""
        folder = filedialog.askdirectory()
        if folder:
            self.temp_path.delete(0, tk.END)
            self.temp_path.insert(0, folder)
            
    def perform_login(self):
        """执行密码登录"""
        account = self.account_entry.get()
        password = self.password_entry.get()
        
        if (account and password and 
            account != "请输入账号" and password != "请输入密码"):
            messagebox.showinfo("登录", "登录成功！")
            self.login_window.destroy()
        else:
            messagebox.showerror("错误", "请输入有效的账号和密码")
            
    def perform_sms_login(self):
        """执行短信登录"""
        phone = self.phone_entry.get()
        code = self.code_entry.get()
        
        if (phone and code and 
            phone != "请输入手机号" and code != "请输入验证码"):
            messagebox.showinfo("登录", "登录成功！")
            self.login_window.destroy()
        else:
            messagebox.showerror("错误", "请输入有效的手机号和验证码")
            
    def show_about(self):
        """显示关于信息"""
        about_text = (
            "Bilibili下载器客户端\n\n"
            "版本: 2.0.0\n"
            "作者: AI Assistant\n\n"
            "功能特性:\n"
            "• 支持多种视频格式下载\n"
            "• 智能链接识别\n"
            "• 批量下载管理\n"
            "• 用户友好界面\n\n"
            "© 2025 All Rights Reserved"
        )
        messagebox.showinfo("关于", about_text)
        
    def run(self):
        """运行应用"""
        # 延迟显示登录窗口
        self.root.after(1000, self.show_login_page)
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 启动主循环
        self.root.mainloop()
        
    def on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出应用吗？"):
            self.root.destroy()

if __name__ == "__main__":
    try:
        app = BilibiliDownloaderClient()
        app.run()
    except Exception as e:
        print(f"应用启动失败: {e}")
        messagebox.showerror("错误", f"应用启动失败: {e}")