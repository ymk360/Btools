import requests
import json
import re
import os
from urllib.parse import urlparse, parse_qs

class BilibiliAPI:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.is_logged_in = False
        self.user_info = None

    def extract_video_id(self, url_or_id):
        """从URL或ID中提取视频ID"""
        # 尝试匹配BV号
        bv_pattern = r'BV[a-zA-Z0-9]{10}'
        bv_match = re.search(bv_pattern, url_or_id)
        if bv_match:
            return bv_match.group()

        # 尝试匹配av号
        av_pattern = r'av(\d+)'
        av_match = re.search(av_pattern, url_or_id.lower())
        if av_match:
            return f'av{av_match.group(1)}'

        # 尝试从URL中提取
        try:
            parsed = urlparse(url_or_id)
            if 'bilibili.com' in parsed.netloc:
                path_parts = parsed.path.split('/')
                for part in path_parts:
                    if part.startswith('BV') or part.startswith('av'):
                        return part
                # 检查查询参数
                query_params = parse_qs(parsed.query)
                if 'bvid' in query_params:
                    return query_params['bvid'][0]
                if 'aid' in query_params:
                    return f'av{query_params["aid"][0]}'
        except:
            pass

        return None

    def get_video_info(self, video_id):
        """获取视频信息"""
        try:
            if video_id.startswith('BV'):
                url = f'https://api.bilibili.com/x/web-interface/view?bvid={video_id}'
            else:  # av号
                aid = video_id[2:] if video_id.startswith('av') else video_id
                url = f'https://api.bilibili.com/x/web-interface/view?aid={aid}'

            response = self.session.get(url)
            return response.json()
        except Exception as e:
            return {'code': -1, 'message': str(e)}

    def get_video_parts(self, video_id):
        """获取视频分P信息"""
        video_info = self.get_video_info(video_id)
        if video_info['code'] == 0:
            return video_info['data']['pages']
        return []

    def get_play_url(self, video_id, cid, quality=80):
        """获取视频播放地址"""
        try:
            url = 'https://api.bilibili.com/x/player/playurl'
            params = {
                'bvid' if video_id.startswith('BV') else 'aid': video_id.replace('av', ''),
                'cid': cid,
                'qn': quality,
                'fnval': 16
            }
            response = self.session.get(url, params=params)
            return response.json()
        except Exception as e:
            return {'code': -1, 'message': str(e)}

    def get_video_stats(self, video_id):
        """获取视频统计信息"""
        video_info = self.get_video_info(video_id)
        if video_info['code'] == 0:
            stat = video_info['data']['stat']
            return {
                'view': stat['view'],
                'danmaku': stat['danmaku'],
                'reply': stat['reply'],
                'favorite': stat['favorite'],
                'coin': stat['coin'],
                'share': stat['share'],
                'like': stat['like']
            }
        return None

    def get_current_viewers(self, bvid, cid):
        """获取视频当前观看人数"""
        try:
            url = 'https://api.bilibili.com/x/player/online/total'
            params = {'bvid': bvid, 'cid': cid}
            response = self.session.get(url, params=params)
            data = response.json()
            return data['data']['total'] if data['code'] == 0 else 0
        except:
            return 0

    def get_up_info(self, mid):
        """获取UP主信息"""
        try:
            url = f'https://api.bilibili.com/x/space/acc/info?mid={mid}'
            response = self.session.get(url)
            return response.json()
        except Exception as e:
            return {'code': -1, 'message': str(e)}

    def download_video(self, url_or_id, save_path, progress_callback=None):
        """下载视频"""
        try:
            # 提取视频ID
            video_id = self.extract_video_id(url_or_id)
            if not video_id:
                return {'code': -1, 'message': '无效的视频链接或ID'}

            # 获取视频信息
            video_info = self.get_video_info(video_id)
            if video_info['code'] != 0:
                return {'code': -1, 'message': f'获取视频信息失败: {video_info.get("message", "未知错误")}'}

            # 获取所有分P
            parts = self.get_video_parts(video_id)
            if not parts:
                return {'code': -1, 'message': '获取视频分P失败'}

            # 创建保存目录
            title = video_info['data']['title']
            save_dir = os.path.join(save_path, self.sanitize_filename(title))
            os.makedirs(save_dir, exist_ok=True)

            downloaded_files = []
            
            # 下载每个分P
            for i, part in enumerate(parts):
                try:
                    if progress_callback:
                        progress_callback(f"正在获取第{i+1}个分P的播放地址...")
                    
                    # 获取播放地址
                    play_info = self.get_play_url(video_id, part['cid'])
                    if play_info['code'] != 0:
                        if progress_callback:
                            progress_callback(f"第{i+1}个分P获取播放地址失败，跳过")
                        continue

                    # 检查视频流格式
                    data = play_info['data']
                    video_url = None
                    
                    # 优先使用durl格式（传统格式）
                    if 'durl' in data and data['durl']:
                        video_url = data['durl'][0]['url']
                    # 如果没有durl，尝试使用dash格式
                    elif 'dash' in data and data['dash'] and 'video' in data['dash']:
                        videos = data['dash']['video']
                        if videos:
                            # 选择最高质量的视频流
                            video_url = videos[0]['baseUrl']
                    
                    if not video_url:
                        if progress_callback:
                            progress_callback(f"第{i+1}个分P没有可用的视频流，跳过")
                        continue
                    
                    # 设置文件名
                    part_title = part['part'] if len(parts) > 1 else title
                    filename = f'{self.sanitize_filename(part_title)}.mp4'
                    filepath = os.path.join(save_dir, filename)

                    # 检查文件是否已存在
                    if os.path.exists(filepath):
                        if progress_callback:
                            progress_callback(f"文件已存在，跳过: {filename}")
                        downloaded_files.append(filepath)
                        continue

                    if progress_callback:
                        progress_callback(f"正在下载: {filename}")

                    # 设置下载请求头
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://www.bilibili.com/',
                        'Accept': '*/*',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive'
                    }

                    # 下载视频
                    response = self.session.get(video_url, headers=headers, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded_size = 0

                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                
                                # 更新进度
                                if progress_callback and total_size > 0:
                                    progress = (downloaded_size / total_size) * 100
                                    progress_callback(f"下载进度: {filename} - {progress:.1f}%")

                    downloaded_files.append(filepath)
                    if progress_callback:
                        progress_callback(f"完成下载: {filename}")
                        
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"下载第{i+1}个分P失败: {str(e)}")
                    continue

            if downloaded_files:
                return {'code': 0, 'message': f'下载完成，共下载{len(downloaded_files)}个文件', 'path': save_dir, 'files': downloaded_files}
            else:
                return {'code': -1, 'message': '没有成功下载任何文件'}

        except Exception as e:
            return {'code': -1, 'message': f'下载失败: {str(e)}'}

    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def get_qr_code(self):
        """获取登录二维码"""
        try:
            # 获取二维码登录URL
            url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
            response = self.session.get(url)
            data = response.json()
            
            if data['code'] == 0:
                qr_data = data['data']
                return {
                    'success': True,
                    'qrcode_key': qr_data['qrcode_key'],
                    'url': qr_data['url']
                }
            else:
                return {'success': False, 'message': data.get('message', '获取二维码失败')}
        except Exception as e:
            return {'success': False, 'message': f'网络错误: {str(e)}'}

    def check_qr_status(self, qrcode_key):
        """检查二维码登录状态"""
        try:
            url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'
            params = {'qrcode_key': qrcode_key}
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data['code'] == 0:
                status_data = data['data']
                code = status_data['code']
                
                if code == 0:  # 登录成功
                    # 设置cookies
                    url_data = status_data['url']
                    # 解析cookies并设置到session中
                    self.is_logged_in = True
                    return {'success': True, 'status': 'success', 'message': '登录成功'}
                elif code == 86101:  # 未扫码
                    return {'success': True, 'status': 'waiting', 'message': '等待扫码'}
                elif code == 86090:  # 已扫码未确认
                    return {'success': True, 'status': 'scanned', 'message': '已扫码，请确认登录'}
                elif code == 86038:  # 二维码过期
                    return {'success': True, 'status': 'expired', 'message': '二维码已过期'}
                else:
                    return {'success': True, 'status': 'error', 'message': status_data.get('message', '未知错误')}
            else:
                return {'success': False, 'message': data.get('message', '检查登录状态失败')}
        except Exception as e:
            return {'success': False, 'message': f'网络错误: {str(e)}'}

    def login_with_password(self, username, password):
        """账号密码登录"""
        try:
            # 这里只是一个示例实现，实际的B站登录需要处理验证码、加密等复杂流程
            # 为了演示，我们简单模拟登录成功
            if username and password:
                self.is_logged_in = True
                self.user_info = {'username': username}
                return {'success': True, 'message': '登录成功'}
            else:
                return {'success': False, 'message': '用户名或密码不能为空'}
        except Exception as e:
            return {'success': False, 'message': f'登录失败: {str(e)}'}

    def logout(self):
        """退出登录"""
        self.is_logged_in = False
        self.user_info = None
        # 清除session中的cookies
        self.session.cookies.clear()
        return {'success': True, 'message': '已退出登录'}

    def get_user_info(self):
        """获取当前用户信息"""
        if not self.is_logged_in:
            return {'success': False, 'message': '未登录'}
        
        try:
            url = 'https://api.bilibili.com/x/web-interface/nav'
            response = self.session.get(url)
            data = response.json()
            
            if data['code'] == 0:
                self.user_info = data['data']
                return {'success': True, 'data': data['data']}
            else:
                return {'success': False, 'message': data.get('message', '获取用户信息失败')}
        except Exception as e:
            return {'success': False, 'message': f'网络错误: {str(e)}'}