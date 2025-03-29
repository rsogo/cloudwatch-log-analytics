import re
import json
import statistics
import numpy as np
import csv
import sys

# ログファイルのパス
log_file = "./logs-insights-results.json"

# 正規表現パターン
# "path":"(.*?)" と "responseLatency": "(\d+)"
path_pattern = re.compile(r'"path"\s*:\s*"([^"]+)"')
latency_pattern = re.compile(r'"responseLatency"\s*:\s*"(\d+)"')

def normalize_path(path):
    # 数字部分を {} に置換
    return re.sub(r'/\d+', '/{}', path)

# 各グループごとのレスポンスレイテンシを格納する辞書
results = {}

with open(log_file, "r") as f:
    data = json.load(f)

for entry in data:
    message = entry.get("@message", "")
    path_match = path_pattern.search(message)
    latency_match = latency_pattern.search(message)
    if path_match and latency_match:
        raw_path = path_match.group(1)
        latency = int(latency_match.group(1))
        norm_path = normalize_path(raw_path)
        results.setdefault(norm_path, []).append(latency)

# 各グループごとに統計量を計算
stats = {}
for norm_path, latencies in results.items():
    avg = round(sum(latencies) / len(latencies), 1)
    max_val = max(latencies)
    percentile90 = round(np.percentile(latencies, 90), 1)
    stats[norm_path] = {
        "count": len(latencies),
        "average": avg,
        "max": max_val,
        "90th_percentile": percentile90
    }

# 結果を標準出力にCSV形式で表示
csv_writer = csv.writer(sys.stdout)
# ヘッダーを書き込む
csv_writer.writerow(["Path", "Count", "Average Latency", "Max Latency", "90th Percentile Latency"])
# 各行を書き込む
for norm_path, stat in stats.items():
    csv_writer.writerow([
        norm_path,
        stat["count"],
        stat["average"],
        stat["max"],
        stat["90th_percentile"]
    ])
