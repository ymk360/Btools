#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from bilibili_api import BilibiliAPI

def test_download():
    """测试下载功能"""
    api = BilibiliAPI()
    
    # 测试视频URL（使用一个短视频进行测试）
    test_url = "BV1GJ411x7h7"  # 这是一个测试视频
    save_path = "g:\\Bitools\\downloads"
    
    # 创建下载目录
    os.makedirs(save_path, exist_ok=True)
    
    def progress_callback(message):
        print(f"[进度] {message}")
    
    print("开始测试下载功能...")
    print(f"测试视频: {test_url}")
    print(f"保存路径: {save_path}")
    print("-" * 50)
    
    # 执行下载
    result = api.download_video(test_url, save_path, progress_callback)
    
    print("-" * 50)
    print(f"下载结果: {result}")
    
    if result['code'] == 0:
        print("✅ 下载成功！")
        print(f"保存路径: {result['path']}")
        if 'files' in result:
            print(f"下载文件数: {len(result['files'])}")
            for file in result['files']:
                print(f"  - {file}")
    else:
        print("❌ 下载失败！")
        print(f"错误信息: {result['message']}")

if __name__ == "__main__":
    test_download()