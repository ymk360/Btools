import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from datetime import datetime
import os
from bilibili_api import BilibiliAPI

class BilibiliDownloaderClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Btools")
        self.root.geometry("1200x800")
        # 设置全局样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 配置颜色主题
        self.style.configure('.', background='#2b2b2b', foreground='white')
        self.style.configure('Card.TFrame', background='#3a3a3a', borderwidth=1, relief='solid', padding=10)
        self.style.configure('Dark.TButton', background='#4a4a4a', foreground='white', padding=6, font=('Microsoft YaHei', 10))
        self.style.configure('Dark.TRadiobutton', background='#3a3a3a', foreground='white', font=('Microsoft YaHei', 12))
        self.style.configure('Dark.TEntry', fieldbackground='#4a4a4a', foreground='white', padding=5, font=('Microsoft YaHei', 12))
        self.style.configure('Dark.TLabel', foreground='white', font=('Microsoft YaHei', 10))
        self.style.configure('TProgressbar', thickness=6, troughcolor='#4a4a4a', background='#00a1d6')
        
        self.root.configure(bg='#2b2b2b')
        self.root.resizable(True, True)
        
        # 初始化B站API
        self.api = BilibiliAPI()
        
        # 当前页面状态
        self.current_page = "search"
        
        # 下载任务列表
        self.download_tasks = []
        
        # 下载路径
        self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        
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
        # 清除现有的侧边栏
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.main_frame:
                widget.destroy()
        
        sidebar = ttk.Frame(self.root, style='Card.TFrame', width=60)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # 应用图标
        icon_frame = tk.Frame(sidebar, bg='#1e1e1e', height=60)
        icon_frame.pack(fill=tk.X, pady=10)
        
        # 创建一个简单的图标
        icon_canvas = tk.Canvas(icon_frame, width=40, height=40, bg='#1e1e1e', highlightthickness=0)
        icon_canvas.pack()
        icon_canvas.create_oval(5, 5, 35, 35, fill='#00a1d6', outline='')
        icon_canvas.create_text(20, 20, text='B', fill='white', font=('Arial', 16, 'bold'))
        
        # 导航按钮
        search_btn = ttk.Button(sidebar, text="🔍", style='Dark.TButton', command=self.show_search_page, width=2)
        search_btn.pack(pady=10)
        self.style.map('Dark.TButton', background=[('active', '#0078d4'), ('pressed', '#005a9e')])
        
        download_btn = ttk.Button(sidebar, text="⬇", style='Dark.TButton', command=self.show_download_page, width=2)
        download_btn.pack(pady=10)
        
        # 底部设置按钮
        settings_frame = tk.Frame(sidebar, bg='#1e1e1e')
        settings_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        settings_btn = ttk.Button(settings_frame, text="⚙", style='Dark.TButton', command=self.show_settings_page, width=2)
        settings_btn.pack(pady=5)
        
        about_btn = ttk.Button(settings_frame, text="ℹ", style='Dark.TButton', command=self.show_about, width=2)
        about_btn.pack(pady=5)

    def perform_search(self, event=None):
        """执行搜索"""
        query = self.search_entry.get().strip()
        if query and query != "请输入链接/AV/BV/SS/EP/AU/AM/SID/FID等...":
            try:
                # 获取视频信息
                video_id = self.api.extract_video_id(query)
                if not video_id:
                    messagebox.showerror("错误", "无效的视频链接或ID")
                    return
                
                video_info = self.api.get_video_info(video_id)
                if video_info['code'] != 0:
                    messagebox.showerror("错误", video_info['message'])
                    return
                
                # 添加下载任务
                task = {
                    'title': video_info['data']['title'],
                    'id': video_info['data']['bvid'],
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'progress': 0,
                    'status': '等待中'
                }
                
                self.download_tasks.append(task)
                self.show_download_page()
                
                # 开始下载
                threading.Thread(target=self.start_download, args=(query, task)).start()
                
            except Exception as e:
                messagebox.showerror("错误", f"搜索失败: {str(e)}")

    def start_download(self, url, task):
        """开始下载任务"""
        def progress_callback(message):
            """进度回调函数"""
            task['status'] = message
            # 尝试从消息中提取进度百分比
            if '下载进度:' in message and '%' in message:
                try:
                    progress_str = message.split('-')[-1].strip().replace('%', '')
                    progress = float(progress_str)
                    task['progress'] = progress
                except:
                    pass
            # 在主线程中更新UI
            self.root.after(0, self.update_download_list)
        
        try:
            # 更新任务状态
            task['status'] = '准备下载...'
            task['progress'] = 0
            self.update_download_list()
            
            # 执行下载
            result = self.api.download_video(url, self.download_path, progress_callback)
            
            if result['code'] == 0:
                task['status'] = f'完成 - {result["message"]}'
                task['progress'] = 100
                # 显示成功消息
                self.root.after(0, lambda: messagebox.showinfo("下载完成", 
                    f"{result['message']}\n保存路径: {result['path']}"))
            else:
                task['status'] = f'失败 - {result["message"]}'
                task['progress'] = 0
                # 显示错误消息
                self.root.after(0, lambda: messagebox.showerror("下载失败", result['message']))
                
            self.root.after(0, self.update_download_list)
            
        except Exception as e:
            task['status'] = f'失败 - {str(e)}'
            task['progress'] = 0
            self.root.after(0, lambda: messagebox.showerror("下载失败", str(e)))
            self.root.after(0, self.update_download_list)

    def update_download_list(self):
        """更新下载列表显示"""
        if self.current_page == "download":
            self.show_download_page()

    def auto_detect(self):
        """自动检测剪贴板中的视频链接"""
        try:
            clipboard = self.root.clipboard_get()
            if clipboard:
                video_id = self.api.extract_video_id(clipboard)
                if video_id:
                    self.search_entry.delete(0, tk.END)
                    self.search_entry.insert(0, clipboard)
                    self.perform_search()
                else:
                    messagebox.showinfo("提示", "未检测到有效的视频链接")
        except:
            messagebox.showinfo("提示", "剪贴板中没有内容")

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

    def show_empty_state(self):
        """显示空状态"""
        empty_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        empty_frame.pack(fill=tk.BOTH, expand=True)
        
        # 居中显示空状态
        center_frame = ttk.Frame(empty_frame, style='Card.TFrame')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 空状态图标
        icon_canvas = tk.Canvas(center_frame, width=100, height=100, bg='#2b2b2b', highlightthickness=0)
        icon_canvas.pack()
        
        # 绘制空状态图标
        icon_canvas.create_oval(25, 25, 75, 75, fill='#404040', outline='')
        icon_canvas.create_text(50, 50, text='📱', fill='white', font=('Arial', 30))
        
        empty_text = ttk.Label(center_frame, text="此处列为空～", style='Dark.TLabel', font=('Microsoft YaHei', 14))
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

    def show_search_page(self):
        """显示搜索页面"""
        self.clear_main_frame()
        
        # 搜索框区域
        search_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        search_frame.pack(fill=tk.X, padx=20, pady=20, ipady=5)
        
        # 搜索输入框
        self.search_entry = ttk.Entry(search_frame, style='Dark.TEntry', font=('Microsoft YaHei', 12))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 搜索按钮
        search_btn = ttk.Button(search_frame, text='搜索', style='Dark.TButton', command=self.perform_search)
        search_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 粘贴按钮
        paste_btn = ttk.Button(search_frame, text='粘贴', style='Dark.TButton', command=self.paste_from_clipboard)
        paste_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 显示空状态
        self.show_empty_state()

    def show_download_page(self):
        """显示下载页面"""
        self.clear_main_frame()
        
        # 下载列表区域
        download_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        download_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 如果没有下载任务，显示空状态
        if not hasattr(self, 'download_tasks') or not self.download_tasks:
            self.show_empty_download_state()
            return
        
        # 显示下载任务列表
        for task in self.download_tasks:
            task_frame = ttk.Frame(download_frame, style='Card.TFrame', padding=10)
            task_frame.pack(fill=tk.X, pady=(0, 10))
            
            # 视频标题
            title_label = ttk.Label(task_frame, text=task['title'], style='Dark.TLabel', font=('Microsoft YaHei', 12, 'bold'))
            title_label.pack(anchor=tk.W, padx=10, pady=5)
            
            # 进度条
            progress = ttk.Progressbar(task_frame, length=300, mode='determinate', style='TProgressbar')
            progress.pack(padx=10, pady=5)
            progress['value'] = task.get('progress', 0)
            
            # 状态标签
            status_label = ttk.Label(task_frame, text=task.get('status', '等待中...'), style='Dark.TLabel', font=('Microsoft YaHei', 10))
            status_label.pack(anchor=tk.W, padx=10, pady=5)

    def show_settings_page(self):
        """显示设置页面"""
        self.clear_main_frame()
        
        settings_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 下载路径设置
        path_frame = tk.Frame(settings_frame, bg='#2b2b2b')
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        path_label = ttk.Label(path_frame, text='下载路径：', style='Dark.TLabel', font=('Microsoft YaHei', 12))
        path_label.pack(side=tk.LEFT)
        
        path_entry = ttk.Entry(path_frame, style='Dark.TEntry')
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        path_entry.insert(0, self.download_path)
        
        browse_btn = ttk.Button(path_frame, text='浏览', style='Dark.TButton', command=self.browse_download_path)
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 其他设置选项可以在这里添加

    def show_login_page(self):
        """显示登录页面"""
        self.clear_main_frame()
        
        login_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        login_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡
        tab_frame = tk.Frame(login_frame, bg='#2b2b2b')
        tab_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # 选项卡按钮
        self.login_mode = tk.StringVar(value='qr')
        
        qr_tab = ttk.Radiobutton(tab_frame, text='扫码登录', variable=self.login_mode, value='qr', style='Dark.TRadiobutton', command=self.switch_login_mode)
        qr_tab.pack(side=tk.LEFT, padx=(0, 20))
        
        pwd_tab = ttk.Radiobutton(tab_frame, text='账号登录', variable=self.login_mode, value='password', style='Dark.TRadiobutton', command=self.switch_login_mode)
        pwd_tab.pack(side=tk.LEFT)
        
        # 登录内容区域
        self.login_content_frame = tk.Frame(login_frame, bg='#2b2b2b')
        self.login_content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 默认显示二维码登录
        self.show_qr_login()
        
    def switch_login_mode(self):
        """切换登录模式"""
        # 安全地清空内容区域
        try:
            for widget in self.login_content_frame.winfo_children():
                widget.destroy()
        except:
            pass
            
        if self.login_mode.get() == 'qr':
            self.show_qr_login()
        else:
            self.show_password_login()
            
    def show_qr_login(self):
        """显示二维码登录界面"""
        # 居中显示登录内容
        center_frame = tk.Frame(self.login_content_frame, bg='#2b2b2b')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 登录标题
        title_label = ttk.Label(center_frame, text='扫码登录', style='Dark.TLabel', font=('Microsoft YaHei', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 二维码显示区域
        self.qr_frame = tk.Frame(center_frame, bg='white', width=200, height=200)
        self.qr_frame.pack(pady=(0, 20))
        self.qr_frame.pack_propagate(False)
        
        # 状态标签
        self.qr_status_label = ttk.Label(center_frame, text='正在生成二维码...', style='Dark.TLabel')
        self.qr_status_label.pack(pady=(0, 10))
        
        # 刷新按钮
        refresh_btn = ttk.Button(center_frame, text='刷新二维码', style='Dark.TButton', command=self.refresh_qr_code)
        refresh_btn.pack()
        
        # 生成二维码
        self.generate_qr_code()
        
    def show_password_login(self):
        """显示账号密码登录界面"""
        # 居中显示登录内容
        center_frame = tk.Frame(self.login_content_frame, bg='#2b2b2b')
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # 登录标题
        title_label = tk.Label(center_frame, text='账号登录', bg='#2b2b2b',
                              fg='white', font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 30))
        
        # 用户名输入
        username_frame = tk.Frame(center_frame, bg='#2b2b2b')
        username_frame.pack(fill=tk.X, pady=(0, 15))
        
        username_label = ttk.Label(username_frame, text='用户名：', style='Dark.TLabel')
        username_label.pack(anchor=tk.W)
        
        self.username_entry = ttk.Entry(username_frame, style='Dark.TEntry', width=30)
        self.username_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 密码输入
        password_frame = tk.Frame(center_frame, bg='#2b2b2b')
        password_frame.pack(fill=tk.X, pady=(0, 20))
        
        password_label = ttk.Label(password_frame, text='密码：', style='Dark.TLabel')
        password_label.pack(anchor=tk.W)
        
        self.password_entry = ttk.Entry(password_frame, style='Dark.TEntry', width=30, show='*')
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 登录按钮
        login_btn = ttk.Button(center_frame, text='登录', style='Dark.TButton', width=20, command=self.perform_password_login)
        login_btn.pack(pady=(10, 0))
        
        # 绑定回车键
        self.password_entry.bind('<Return>', lambda e: self.perform_password_login())
        
    def generate_qr_code(self):
        """生成二维码"""
        def generate():
            result = self.api.get_qr_code()
            if result['success']:
                self.qrcode_key = result['qrcode_key']
                qr_url = result['url']
                
                # 更新状态
                self.qr_status_label.config(text='请使用哔哩哔哩手机客户端扫码登录')
                
                # 在二维码区域显示URL（实际应用中可以生成真正的二维码图片）
                qr_text = tk.Text(self.qr_frame, bg='white', fg='black',
                                 font=('Arial', 8), wrap=tk.WORD)
                qr_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                qr_text.insert(tk.END, f'二维码内容：\n{qr_url}')
                qr_text.config(state=tk.DISABLED)
                
                # 开始检查登录状态
                self.check_qr_login_status()
            else:
                self.qr_status_label.config(text=f'生成二维码失败：{result["message"]}')
                
        threading.Thread(target=generate, daemon=True).start()
        
    def check_qr_login_status(self):
        """检查二维码登录状态"""
        def check():
            if hasattr(self, 'qrcode_key'):
                result = self.api.check_qr_status(self.qrcode_key)
                if result['success']:
                    status = result['status']
                    message = result['message']
                    
                    self.qr_status_label.config(text=message)
                    
                    if status == 'success':
                        messagebox.showinfo('登录成功', '登录成功！')
                        self.show_search_page()  # 跳转到搜索页面
                        return
                    elif status == 'expired':
                        return  # 二维码过期，停止检查
                    
                    # 继续检查状态
                    self.root.after(2000, self.check_qr_login_status)
                else:
                    self.qr_status_label.config(text=f'检查状态失败：{result["message"]}')
                    
        threading.Thread(target=check, daemon=True).start()
        
    def refresh_qr_code(self):
        """刷新二维码"""
        # 安全地清空二维码区域
        try:
            for widget in self.qr_frame.winfo_children():
                widget.destroy()
        except:
            pass
            
        try:
            self.qr_status_label.config(text='正在生成二维码...')
        except:
            pass
        self.generate_qr_code()
        
    def perform_password_login(self):
        """执行账号密码登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror('错误', '请输入用户名和密码')
            return
            
        def login():
            result = self.api.login_with_password(username, password)
            if result['success']:
                messagebox.showinfo('登录成功', result['message'])
                self.show_search_page()  # 跳转到搜索页面
            else:
                messagebox.showerror('登录失败', result['message'])
                
        threading.Thread(target=login, daemon=True).start()

    def on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出应用吗？"):
            self.root.destroy()

    def paste_from_clipboard(self):
        """从剪贴板粘贴内容"""
        try:
            clipboard = self.root.clipboard_get()
            if clipboard:
                self.search_entry.delete(0, tk.END)
                self.search_entry.insert(0, clipboard)
        except:
            messagebox.showinfo("提示", "剪贴板中没有内容")

    def browse_download_path(self):
        """浏览并选择下载路径"""
        path = filedialog.askdirectory()
        if path:
            self.download_path = path
            # 更新输入框内容
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for grandchild in child.winfo_children():
                                if isinstance(grandchild, tk.Entry):
                                    grandchild.delete(0, tk.END)
                                    grandchild.insert(0, path)

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "清风.exe - B站视频下载工具\n\n版本：1.0.0\n作者：清风\n")

    def run(self):
        """运行应用"""
        # 延迟显示登录窗口
        self.root.after(1000, self.show_login_page)
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 启动主循环
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = BilibiliDownloaderClient()
        app.run()
    except Exception as e:
        print(f"应用启动失败: {e}")
        messagebox.showerror("错误", f"应用启动失败: {e}")