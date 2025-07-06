#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from bilibili_api import BilibiliAPI

def debug_api():
    """调试API功能"""
    api = BilibiliAPI()
    
    # 测试视频
    test_url = "BV1GJ411x7h7"
    
    print("=== 调试Bilibili API ===")
    print(f"测试视频: {test_url}")
    print()
    
    # 1. 提取视频ID
    video_id = api.extract_video_id(test_url)
    print(f"1. 提取的视频ID: {video_id}")
    print()
    
    # 2. 获取视频信息
    video_info = api.get_video_info(video_id)
    print(f"2. 视频信息:")
    print(json.dumps(video_info, indent=2, ensure_ascii=False))
    print()
    
    if video_info['code'] == 0:
        # 3. 获取视频分P
        parts = api.get_video_parts(video_id)
        print(f"3. 视频分P:")
        print(json.dumps(parts, indent=2, ensure_ascii=False))
        print()
        
        if parts:
            # 4. 获取播放地址
            first_part = parts[0]
            cid = first_part['cid']
            print(f"4. 获取播放地址 (cid: {cid}):")
            
            play_info = api.get_play_url(video_id, cid)
            print(json.dumps(play_info, indent=2, ensure_ascii=False))
            print()
            
            # 5. 检查数据结构
            if play_info['code'] == 0:
                data = play_info['data']
                print(f"5. 数据结构分析:")
                print(f"   - 包含 'durl': {'durl' in data}")
                print(f"   - 包含 'dash': {'dash' in data}")
                if 'durl' in data:
                    print(f"   - durl 长度: {len(data['durl'])}")
                    if data['durl']:
                        print(f"   - 第一个durl: {data['durl'][0]}")
                if 'dash' in data:
                    print(f"   - dash 内容: {data['dash']}")
            else:
                print(f"获取播放地址失败: {play_info['message']}")
    else:
        print(f"获取视频信息失败: {video_info['message']}")

if __name__ == "__main__":
    debug_api()