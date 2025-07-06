import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
import os
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
import os

class BilibiliDownloaderClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Btools")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # 当前页面状态
        self.current_page = "search"
        
        # 下载任务列表
        self.download_tasks = []
        
        # 创建主界面
        self.create_main_interface()
        
    def configure_styles(self):
        """配置界面样式"""
        # 配置深色主题
        self.style.configure('Dark.TFrame', background='#2b2b2b')
        self.style.configure('Card.TFrame', background='#3a3a3a', borderwidth=1, relief='solid')
        self.style.configure('Dark.TEntry', background='#404040', foreground='white', padding=8, font=('Microsoft YaHei', 10))
        self.style.configure('Dark.TLabel', background='#2b2b2b', foreground='white', font=('Microsoft YaHei', 10))
        self.style.configure('TProgressbar', thickness=6, troughcolor='#404040', background='#0078d4')
        self.style.configure('Dark.TButton', background='#404040', foreground='white', padding=6, font=('Microsoft YaHei', 10))
        self.style.map('Dark.TButton', background=[('active', '#0078d4'), ('hover', '#505050')])
        self.style.configure('Dark.TEntry', background='#404040', foreground='white')
        
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
        
        # 创建一个简单的图标
        icon_label = tk.Label(icon_frame, text="🎬", bg='#1e1e1e', fg='white', font=('Arial', 20))
        icon_label.pack()
        
        # 搜索按钮
        search_btn = ttk.Button(sidebar, text="🔍", style='Dark.TButton', 
                              command=self.show_search_page, width=2)
        search_btn.pack(pady=10)
        
        # 下载按钮
        download_btn = ttk.Button(sidebar, text="⬇", style='Dark.TButton', 
                                command=self.show_download_page, width=2)
        download_btn.pack(pady=10)
        
        # 底部设置按钮
        settings_frame = tk.Frame(sidebar, bg='#1e1e1e')
        settings_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        settings_btn = ttk.Button(settings_frame, text="⚙", style='Dark.TButton', 
                                command=self.show_settings_page, width=2)
        settings_btn.pack(pady=5)
        
        about_btn = ttk.Button(settings_frame, text="ℹ", style='Dark.TButton', 
                             command=self.show_about, width=2)
        about_btn.pack(pady=5)
        
    def clear_main_frame(self):
        """清空主内容区域"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
    def show_search_page(self):
        """显示搜索页面"""
        self.current_page = "search"
        self.clear_main_frame()
        
        # 搜索框区域
        search_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        search_frame.pack(fill=tk.X, padx=20, pady=20, ipady=15)
        
        # 搜索输入框
        self.search_entry = ttk.Entry(search_frame, style='Dark.TEntry', 
                                    font=('Microsoft YaHei', 12), relief=tk.FLAT, bd=0, insertbackground='white')
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 10))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.search_entry.insert(0, "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...")
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<Return>', self.perform_search)
        
        # 自动检测按钮
        auto_detect_btn = tk.Button(search_frame, text="自动检测", bg='#0078d4', fg='white', 
                                   font=('Microsoft YaHei', 10), relief=tk.FLAT, command=self.auto_detect, padx=15)
        auto_detect_btn.pack(side=tk.RIGHT, padx=(10, 0), ipady=5, ipadx=10)
        
        # 搜索按钮
        search_btn = tk.Button(search_frame, text="🔍", bg='#404040', fg='white', 
                              font=('Arial', 12), relief=tk.FLAT, command=self.perform_search)
        search_btn.pack(side=tk.RIGHT, padx=(5, 0), ipady=5, ipadx=10)
        
        # 空状态显示
        self.show_empty_state()
        
    def show_download_page(self):
        """显示下载页面"""
        self.current_page = "download"
        self.clear_main_frame()
        
        # 顶部标签栏
        tab_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        tab_frame.pack(fill=tk.X, padx=20, pady=(20, 0), ipady=10)
        
        # 标签按钮
        waiting_btn = tk.Button(tab_frame, text="等待中", bg='#2b2b2b', fg='#888', 
                               font=('Arial', 12), relief=tk.FLAT, border=0)
        waiting_btn.pack(side=tk.LEFT, padx=(0, 20), pady=5)

        progress_btn = tk.Button(tab_frame, text="进行中", bg='#2b2b2b', fg='#888', 
                                font=('Microsoft YaHei', 12), relief=tk.FLAT, border=0)
        progress_btn.pack(side=tk.LEFT, padx=(0, 20), pady=5)

        completed_btn = tk.Button(tab_frame, text="已完成", bg='#2b2b2b', fg='#0078d4', 
                                 font=('Microsoft YaHei', 12, 'bold'), relief=tk.FLAT, border=0, 
                                 highlightthickness=1, highlightbackground='#0078d4', highlightcolor='#0078d4')
        completed_btn.pack(side=tk.LEFT)
        
        # 下载列表区域
        if self.download_tasks:
            self.show_download_list()
        else:
            self.show_empty_download_state()
            
    def show_settings_page(self):
        """显示设置页面"""
        self.current_page = "settings"
        self.clear_main_frame()
        
        # 设置标题
        title_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        title_frame.pack(fill=tk.X, padx=20, pady=20, ipady=10)
        
        settings_icon = tk.Label(title_frame, text="⚙", bg='#3a3a3a', fg='white', font=('Microsoft YaHei', 16))
        settings_icon.pack(side=tk.LEFT)
        
        settings_title = tk.Label(title_frame, text="设置", bg='#3a3a3a', fg='white', font=('Microsoft YaHei', 16))
        settings_title.pack(side=tk.LEFT, padx=(10, 0))
        
        help_btn = tk.Button(title_frame, text="?", bg='#2b2b2b', fg='#888', 
                            font=('Arial', 12), relief=tk.FLAT, border=0)
        help_btn.pack(side=tk.RIGHT)
        
        # 设置内容
        content_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20), ipady=15, ipadx=15)
        
        # 保存路径设置
        path_frame = tk.Frame(content_frame, bg='#2b2b2b')
        path_frame.pack(fill=tk.X, pady=10)
        
        path_icon = tk.Label(path_frame, text="📁", bg='#2b2b2b', fg='white', font=('Arial', 12))
        path_icon.pack(side=tk.LEFT)
        
        path_label = tk.Label(path_frame, text="保存路径", bg='#3a3a3a', fg='white', font=('Microsoft YaHei', 12))
        path_label.pack(side=tk.LEFT, padx=(10, 0))
        
        save_btn = tk.Button(path_frame, text="存储", bg='#2b2b2b', fg='white', 
                            font=('Arial', 10), relief=tk.FLAT, border=0)
        save_btn.pack(side=tk.RIGHT)
        
        # 输出文件路径
        output_frame = tk.Frame(content_frame, bg='#2b2b2b')
        output_frame.pack(fill=tk.X, pady=5)
        
        output_label = tk.Label(output_frame, text="输出文件", bg='#3a3a3a', fg='white', font=('Microsoft YaHei', 10))
        output_label.pack(anchor=tk.W)
        
        self.output_path = tk.Entry(output_frame, bg='#404040', fg='white', 
                                   font=('Arial', 10), relief=tk.FLAT)
        self.output_path.pack(fill=tk.X, ipady=8)
        self.output_path.insert(0, "C:\\Users\\hhhjh\\Desktop")
        
        browse_btn = tk.Button(output_frame, text="📁", bg='#0078d4', fg='white', 
                              font=('Arial', 10), relief=tk.FLAT, command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        download_btn = tk.Button(output_frame, text="下载", bg='#2b2b2b', fg='white', 
                                font=('Arial', 10), relief=tk.FLAT, border=0)
        download_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 临时文件路径
        temp_frame = tk.Frame(content_frame, bg='#2b2b2b')
        temp_frame.pack(fill=tk.X, pady=5)
        
        temp_label = tk.Label(temp_frame, text="临时文件", bg='#2b2b2b', fg='white', font=('Arial', 10))
        temp_label.pack(anchor=tk.W)
        
        temp_desc = tk.Label(temp_frame, text="应用首先下载至此文件夹，随后会处理转移至输出文件夹。", 
                            bg='#2b2b2b', fg='#888', font=('Arial', 9))
        temp_desc.pack(anchor=tk.W)
        
        self.temp_path = tk.Entry(temp_frame, bg='#404040', fg='white', 
                                 font=('Arial', 10), relief=tk.FLAT)
        self.temp_path.pack(fill=tk.X, ipady=5)
        self.temp_path.insert(0, "C:\\Users\\hhhjh\\AppData\\Local\\Temp\\")
        
        temp_browse_btn = tk.Button(temp_frame, text="📁", bg='#0078d4', fg='white', 
                                   font=('Arial', 10), relief=tk.FLAT, command=self.browse_temp_folder)
        temp_browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 缓存设置
        cache_frame = tk.Frame(content_frame, bg='#2b2b2b')
        cache_frame.pack(fill=tk.X, pady=20)
        
        cache_icon = tk.Label(cache_frame, text="💾", bg='#2b2b2b', fg='white', font=('Arial', 12))
        cache_icon.pack(side=tk.LEFT)
        
        cache_label = tk.Label(cache_frame, text="缓存", bg='#2b2b2b', fg='white', font=('Arial', 12))
        cache_label.pack(side=tk.LEFT, padx=(10, 0))
        
        cache_desc = tk.Label(cache_frame, text="用户数据缓存有每条信息，下载记录等重要数据，切勿随意删除。", 
                             bg='#2b2b2b', fg='#888', font=('Arial', 9))
        cache_desc.pack(anchor=tk.W, pady=(5, 0))
        
        # 缓存项目
        cache_items = [
            ("日志", "23.62 KB"),
            ("临时文件", "0.00 KB"),
            ("Webview", "38.53 MB"),
            ("用户数据库", "28.00 KB")
        ]
        
        for item_name, item_size in cache_items:
            item_frame = tk.Frame(content_frame, bg='#2b2b2b')
            item_frame.pack(fill=tk.X, pady=2)
            
            name_label = tk.Label(item_frame, text=item_name, bg='#2b2b2b', fg='white', font=('Arial', 10))
            name_label.pack(side=tk.LEFT)
            
            clean_btn = tk.Button(item_frame, text="🗑", bg='#0078d4', fg='white', 
                                 font=('Arial', 10), relief=tk.FLAT)
            clean_btn.pack(side=tk.RIGHT)
            
            size_label = tk.Label(item_frame, text=item_size, bg='#2b2b2b', fg='#888', font=('Arial', 10))
            size_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # 语言设置
        lang_frame = tk.Frame(content_frame, bg='#2b2b2b')
        lang_frame.pack(fill=tk.X, pady=20)
        
        lang_icon = tk.Label(lang_frame, text="🌐", bg='#2b2b2b', fg='white', font=('Arial', 12))
        lang_icon.pack(side=tk.LEFT)
        
        lang_label = tk.Label(lang_frame, text="语言", bg='#2b2b2b', fg='white', font=('Arial', 12))
        lang_label.pack(side=tk.LEFT, padx=(10, 0))
        
        lang_var = tk.StringVar(value="简体中文 cn")
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var, state="readonly", 
                                 values=["简体中文 cn", "English en"])
        lang_combo.pack(side=tk.RIGHT)
        
    def show_login_page(self):
        """显示登录页面"""
        login_window = tk.Toplevel(self.root)
        login_window.title("登录")
        login_window.geometry("800x600")
        login_window.configure(bg='#2b2b2b')
        login_window.transient(self.root)
        login_window.grab_set()
        
        # 居中显示
        login_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 200, self.root.winfo_rooty() + 100))
        
        main_frame = tk.Frame(login_window, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # 左侧二维码区域
        left_frame = tk.Frame(main_frame, bg='#2b2b2b')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 50))
        
        qr_title = tk.Label(left_frame, text="扫描二维码登录", bg='#2b2b2b', fg='white', font=('Arial', 16))
        qr_title.pack(pady=(0, 20))
        
        # 二维码占位符
        qr_frame = tk.Frame(left_frame, bg='white', width=200, height=200)
        qr_frame.pack(pady=20)
        qr_frame.pack_propagate(False)
        
        qr_label = tk.Label(qr_frame, text="QR Code\nPlaceholder", bg='white', fg='black', font=('Arial', 12))
        qr_label.pack(expand=True)
        
        qr_desc1 = tk.Label(left_frame, text="请使用", bg='#2b2b2b', fg='#888', font=('Arial', 10))
        qr_desc1.pack()
        
        qr_desc2 = tk.Label(left_frame, text="哔哩哔哩客户端", bg='#2b2b2b', fg='#0078d4', font=('Arial', 10))
        qr_desc2.pack()
        
        qr_desc3 = tk.Label(left_frame, text="扫码登录或点击下载APP", bg='#2b2b2b', fg='#888', font=('Arial', 10))
        qr_desc3.pack()
        
        # 底部卡通形象
        char_label = tk.Label(left_frame, text="🎭", bg='#2b2b2b', fg='white', font=('Arial', 30))
        char_label.pack(side=tk.BOTTOM, pady=20)
        
        # 右侧登录表单区域
        right_frame = tk.Frame(main_frame, bg='#2b2b2b')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 登录方式选择
        login_tabs = tk.Frame(right_frame, bg='#2b2b2b')
        login_tabs.pack(fill=tk.X, pady=(0, 30))
        
        pwd_tab = tk.Button(login_tabs, text="密码登录", bg='#2b2b2b', fg='#0078d4', 
                           font=('Arial', 12), relief=tk.FLAT, border=0)
        pwd_tab.pack(side=tk.LEFT, padx=(0, 20))
        
        sms_tab = tk.Button(login_tabs, text="短信登录", bg='#2b2b2b', fg='#888', 
                           font=('Arial', 12), relief=tk.FLAT, border=0)
        sms_tab.pack(side=tk.LEFT)
        
        # 登录表单
        form_frame = tk.Frame(right_frame, bg='#2b2b2b')
        form_frame.pack(fill=tk.X, pady=20)
        
        # 账号输入
        account_label = tk.Label(form_frame, text="账号", bg='#2b2b2b', fg='white', font=('Arial', 12))
        account_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.account_entry = tk.Entry(form_frame, bg='#404040', fg='white', 
                                     font=('Arial', 12), relief=tk.FLAT)
        self.account_entry.pack(fill=tk.X, ipady=10)
        self.account_entry.insert(0, "请输入账号")
        
        # 密码输入
        password_label = tk.Label(form_frame, text="密码", bg='#2b2b2b', fg='white', font=('Arial', 12))
        password_label.pack(anchor=tk.W, pady=(20, 5))
        
        self.password_entry = tk.Entry(form_frame, bg='#404040', fg='white', 
                                      font=('Arial', 12), relief=tk.FLAT, show="*")
        self.password_entry.pack(fill=tk.X, ipady=10)
        self.password_entry.insert(0, "请输入密码")
        
        # 登录按钮
        login_btn = tk.Button(form_frame, text="登录", bg='#0078d4', fg='white', 
                             font=('Arial', 12), relief=tk.FLAT, command=lambda: self.perform_login(login_window))
        login_btn.pack(fill=tk.X, pady=20, ipady=10)
        
        # 协议说明
        agreement_text = "该应用产生与收集的所有数据仅存储于用户本地\n登录即代表同意"
        agreement_label = tk.Label(form_frame, text=agreement_text, bg='#2b2b2b', fg='#888', 
                                  font=('Arial', 9), justify=tk.CENTER)
        agreement_label.pack(pady=10)
        
        # 协议链接
        links_frame = tk.Frame(form_frame, bg='#2b2b2b')
        links_frame.pack()
        
        privacy_link = tk.Label(links_frame, text="隐私政策", bg='#2b2b2b', fg='#0078d4', 
                               font=('Arial', 9), cursor="hand2")
        privacy_link.pack(side=tk.LEFT)
        
        and_label = tk.Label(links_frame, text=" 和 ", bg='#2b2b2b', fg='#888', font=('Arial', 9))
        and_label.pack(side=tk.LEFT)
        
        terms_link = tk.Label(links_frame, text="用户协议", bg='#2b2b2b', fg='#0078d4', 
                             font=('Arial', 9), cursor="hand2")
        terms_link.pack(side=tk.LEFT)
        
        # 底部卡通形象
        char_label2 = tk.Label(right_frame, text="🎪", bg='#2b2b2b', fg='white', font=('Arial', 30))
        char_label2.pack(side=tk.BOTTOM, pady=20)
        
    def show_empty_state(self):
        """显示空状态"""
        empty_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        empty_frame.pack(fill=tk.BOTH, expand=True)
        
        # 居中显示空状态
        center_frame = tk.Frame(empty_frame, bg='#2b2b2b')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 空状态图标
        empty_icon = tk.Label(center_frame, text="📱", bg='#2b2b2b', fg='#666', font=('Arial', 50))
        empty_icon.pack()
        
        empty_text = tk.Label(center_frame, text="此处列为空～", bg='#3a3a3a', fg='#666', font=('Microsoft YaHei', 14))
        empty_text.pack(pady=10)
        
    def show_empty_download_state(self):
        """显示下载页面空状态"""
        empty_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        empty_frame.pack(fill=tk.BOTH, expand=True)
        
        # 居中显示空状态
        center_frame = tk.Frame(empty_frame, bg='#2b2b2b')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 空状态图标
        empty_icon = tk.Label(center_frame, text="📥", bg='#2b2b2b', fg='#666', font=('Arial', 50))
        empty_icon.pack()
        
        empty_text = tk.Label(center_frame, text="暂无下载任务", bg='#3a3a3a', fg='#666', font=('Microsoft YaHei', 14))
        empty_text.pack(pady=10)
        
    def show_download_list(self):
        """显示下载列表"""
        # 示例下载任务
        task_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        task_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 任务信息
        info_frame = tk.Frame(task_frame, bg='#2b2b2b')
        info_frame.pack(fill=tk.X)
        
        title_label = tk.Label(info_frame, text="【Dead Inside】【循环歌单】\"我点炸弹，书桌如心脏狂跳\"", 
                              bg='#2b2b2b', fg='white', font=('Arial', 12))
        title_label.pack(anchor=tk.W)
        
        id_label = tk.Label(info_frame, text="ufs8QchDG87sjZ20", bg='#2b2b2b', fg='#888', font=('Arial', 10))
        id_label.pack(anchor=tk.E)
        
        time_label = tk.Label(info_frame, text="2025-06-28 09:39:01", bg='#2b2b2b', fg='#888', font=('Arial', 10))
        time_label.pack(anchor=tk.W)
        
        # 进度条
        progress_frame = tk.Frame(task_frame, bg='#2b2b2b')
        progress_frame.pack(fill=tk.X, pady=5)
        
        status_label = tk.Label(progress_frame, text="完成", bg='#2b2b2b', fg='white', font=('Arial', 10))
        status_label.pack(side=tk.LEFT)
        
        # 进度条
        progress_bar = ttk.Progressbar(progress_frame, style='TProgressbar', orient='horizontal', length=100, mode='determinate', value=100)
        progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        percent_label = tk.Label(progress_frame, text="100.0 %", bg='#2b2b2b', fg='white', font=('Arial', 10))
        percent_label.pack(side=tk.RIGHT)
        
        # 操作按钮
        action_frame = tk.Frame(task_frame, bg='#2b2b2b')
        action_frame.pack(fill=tk.X, pady=5)
        
        pause_btn = tk.Button(action_frame, text="⏸", bg='#404040', fg='white', 
                             font=('Arial', 12), relief=tk.FLAT)
        pause_btn.pack(side=tk.RIGHT, padx=2)
        
        folder_btn = tk.Button(action_frame, text="📁", bg='#404040', fg='white', 
                              font=('Arial', 12), relief=tk.FLAT)
        folder_btn.pack(side=tk.RIGHT, padx=2)
        
        delete_btn = tk.Button(action_frame, text="🗑", bg='#404040', fg='white', 
                              font=('Arial', 12), relief=tk.FLAT)
        delete_btn.pack(side=tk.RIGHT, padx=2)
        
    def on_search_focus_in(self, event):
        """搜索框获得焦点时清空占位符"""
        if self.search_entry.get() == "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...":
            self.search_entry.delete(0, tk.END)
            
    def perform_search(self, event=None):
        """执行搜索"""
        query = self.search_entry.get().strip()
        if query and query != "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...":
            messagebox.showinfo("搜索", f"正在搜索: {query}")
            # 这里可以添加实际的搜索逻辑
            
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
            
    def perform_login(self, login_window):
        """执行登录"""
        account = self.account_entry.get()
        password = self.password_entry.get()
        
        if account and password and account != "请输入账号" and password != "请输入密码":
            messagebox.showinfo("登录", "登录成功！")
            login_window.destroy()
        else:
            messagebox.showerror("错误", "请输入有效的账号和密码")
            
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "Bilibili下载器客户端\n版本: 1.0.0\n作者: AI Assistant")
        
    def run(self):
        """运行应用"""
        # 显示登录窗口
        self.root.after(1000, self.show_login_page)
        self.root.mainloop()

if __name__ == "__main__":
    app = BilibiliDownloaderClient()
    app.run()