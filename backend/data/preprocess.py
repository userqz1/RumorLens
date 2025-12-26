#!/usr/bin/env python3
"""
Ma-Weibo 数据集预处理脚本
将原始数据转换为统一的 CSV 格式
"""

import json
import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any


def parse_weibo_txt(file_path: str) -> Dict[str, int]:
    """解析 Weibo.txt 获取事件ID和标签映射"""
    event_labels = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                # 格式: eid:10031080900	label:0	...
                eid = parts[0].replace('eid:', '')
                label = int(parts[1].replace('label:', ''))
                event_labels[eid] = label
    return event_labels


def parse_event_json(json_path: str) -> Dict[str, Any]:
    """解析单个事件的 JSON 文件，提取源帖子信息"""
    with open(json_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    if not posts:
        return None

    # 第一个帖子是源帖子（原始声明）
    source_post = posts[0]

    return {
        'event_id': source_post.get('id'),
        'text': source_post.get('text', ''),
        'original_text': source_post.get('original_text', ''),
        'username': source_post.get('username', ''),
        'screen_name': source_post.get('screen_name', ''),
        'uid': source_post.get('uid'),
        'verified': source_post.get('verified', False),
        'followers_count': source_post.get('followers_count', 0),
        'reposts_count': source_post.get('reposts_count', 0),
        'comments_count': source_post.get('comments_count', 0),
        'attitudes_count': source_post.get('attitudes_count', 0),
        'timestamp': source_post.get('t'),
        'total_posts': len(posts),  # 传播链中的总帖子数
    }


def preprocess_dataset(raw_dir: str, output_path: str):
    """预处理整个数据集"""
    raw_path = Path(raw_dir)
    weibo_txt = raw_path / 'Weibo.txt'
    weibo_dir = raw_path / 'Weibo'

    # 解析标签
    print("解析事件标签...")
    event_labels = parse_weibo_txt(str(weibo_txt))
    print(f"共 {len(event_labels)} 个事件")

    # 统计标签分布
    rumor_count = sum(1 for v in event_labels.values() if v == 1)
    non_rumor_count = len(event_labels) - rumor_count
    print(f"谣言: {rumor_count}, 非谣言: {non_rumor_count}")

    # 解析每个事件
    records = []
    for eid, label in event_labels.items():
        json_path = weibo_dir / f"{eid}.json"
        if not json_path.exists():
            print(f"警告: 未找到 {eid}.json")
            continue

        try:
            event_data = parse_event_json(str(json_path))
            if event_data:
                event_data['label'] = label
                event_data['is_rumor'] = label == 1
                records.append(event_data)
        except Exception as e:
            print(f"解析 {eid}.json 时出错: {e}")

    # 创建 DataFrame
    df = pd.DataFrame(records)

    # 保存到 CSV
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"\n预处理完成!")
    print(f"总记录数: {len(df)}")
    print(f"输出文件: {output_path}")
    print(f"\n数据集统计:")
    print(df.describe())

    return df


def main():
    # 路径配置
    script_dir = Path(__file__).parent
    raw_dir = script_dir / 'raw'
    processed_dir = script_dir / 'processed'
    output_path = processed_dir / 'weibo_rumors.csv'

    # 预处理
    df = preprocess_dataset(str(raw_dir), str(output_path))

    # 输出样例
    print("\n\n样例数据 (前5条):")
    print(df[['event_id', 'text', 'is_rumor', 'total_posts']].head())


if __name__ == '__main__':
    main()
