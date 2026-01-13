# 数据库结构说明 (sensecraft_voice_public)

## 数据库连接信息
- 主机: 119.147.208.104
- 端口: 41030
- 用户名: root
- 数据库: sensecraft_voice_public

---

## 核心表结构

### 1. recordings (语音转录记录表)
**记录数**: 107,415 条

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint(20) | 主键，自增 |
| mac_address | varchar(32) | 设备 MAC 地址，关联 devices 表 |
| speaker_id | varchar(64) | 说话人 ID |
| speaker_name | varchar(128) | 说话人名称 (如: 用户_01) |
| text | text | **转录的文字内容** |
| status | tinyint(4) | 状态 (0: 未处理, 1: 已处理) |
| created_at | bigint(20) | 创建时间戳 (毫秒) |
| device_time | bigint(20) | 设备时间戳 (毫秒) |
| session_id | varchar(128) | 会话 ID |
| audio_id | varchar(64) | 音频文件 ID |

**示例数据**:
```
id: 1521066
mac_address: 2c:cf:67:3b:71:b1
speaker_name: 用户_01
text: 啊，要录点东西，不然怎么讲。
device_time: 1763620925499 (毫秒时间戳)
session_id: 75cf82b50a0fd10c827f5872518fd34f
```

---

### 2. devices (设备表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint(20) | 主键 |
| mac_address | varchar(32) | MAC 地址 (唯一键) |
| name | varchar(128) | **设备名称** (如: 多功能会议室) |
| version | varchar(64) | 固件版本 |
| ip_address | varchar(64) | IP 地址 |
| location_id | bigint(20) | 位置 ID |
| store_id | bigint(20) | 门店 ID |
| created_at | bigint(20) | 创建时间 |
| updated_at | bigint(20) | 更新时间 |

**有名称的设备**:
| MAC 地址 | 名称 | 录音数量 |
|----------|------|----------|
| 2c:cf:67:39:6f:64 | 多功能会议室 | 19,857 |
| 2c:cf:67:4f:8d:f3 | (未命名) | 47,746 |
| 2c:cf:67:40:ac:6d | (未命名) | 29,134 |

---

### 3. audio_sessions (音频会话表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint(20) | 主键 |
| session_id | varchar(64) | 会话 ID (唯一) |
| device_id | varchar(32) | 设备 ID (mac_address) |
| start_time | bigint(20) | 开始时间 |
| end_time | bigint(20) | 结束时间 |
| total_chunks | bigint(20) | 音频块数量 |
| status | tinyint(4) | 状态 |

---

### 4. audio_recordings (音频文件表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | varchar(64) | 主键 |
| session_id | varchar(64) | 会话 ID |
| audio_id | varchar(64) | 音频 ID |
| mac_address | varchar(17) | MAC 地址 |
| file_path | varchar(255) | **音频文件路径** |
| file_size | bigint(20) | 文件大小 |
| upload_time | bigint(20) | 上传时间 |

---

### 5. locations (位置表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint(20) | 主键 |
| store_id | bigint(20) | 所属门店 |
| name | varchar(128) | 位置名称 |
| code | varchar(32) | 位置代码 |

---

### 6. stores (门店表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint(20) | 主键 |
| name | varchar(128) | 门店名称 |
| code | varchar(32) | 门店代码 (唯一) |

---

### 7. keywords (关键词表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint(20) | 主键 |
| keyword | varchar(50) | 关键词 (唯一) |
| synonyms | varchar(500) | 同义词列表 |
| mark_color | varchar(7) | 标记颜色 |

---

### 8. keyword_matches (关键词匹配表)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint(20) | 主键 |
| recording_id | bigint(20) | 关联 recordings.id |
| mac_address | varchar(32) | MAC 地址 |
| keyword_id | bigint(20) | 关联 keywords.id |
| keyword | varchar(50) | 匹配的关键词 |
| matched_text | text | 匹配的文本 |
| match_type | varchar(20) | 匹配类型 (exact) |
| confidence | decimal(3,2) | 置信度 |

---

## 数据关联关系

```
recordings.mac_address ──────> devices.mac_address
recordings.session_id ───────> audio_sessions.session_id
recordings.audio_id ─────────> audio_recordings.audio_id

devices.location_id ─────────> locations.id
devices.store_id ────────────> stores.id
locations.store_id ──────────> stores.id

keyword_matches.recording_id ─> recordings.id
keyword_matches.keyword_id ───> keywords.id
```

---

## 时间戳说明

所有时间字段使用 **毫秒级 Unix 时间戳**:
- `device_time: 1763620925499` = 2026-01-10 某时刻
- 转换: `datetime.fromtimestamp(device_time / 1000)`

---

## 常用查询示例

### 查询设备列表
```sql
SELECT
  d.mac_address,
  IFNULL(NULLIF(d.name, ''), d.mac_address) as display_name,
  COUNT(r.id) as recording_count
FROM devices d
LEFT JOIN recordings r ON d.mac_address = r.mac_address
GROUP BY d.mac_address
ORDER BY recording_count DESC;
```

### 按设备和时间范围查询转录记录
```sql
SELECT
  r.id,
  r.speaker_name,
  r.text,
  FROM_UNIXTIME(r.device_time / 1000) as time,
  r.session_id
FROM recordings r
JOIN devices d ON r.mac_address = d.mac_address
WHERE (d.name = '设备名称' OR d.mac_address = '设备MAC')
  AND r.device_time >= {start_timestamp_ms}
  AND r.device_time <= {end_timestamp_ms}
ORDER BY r.device_time ASC;
```

### 统计每日录音数量
```sql
SELECT
  DATE(FROM_UNIXTIME(device_time/1000)) as date,
  COUNT(*) as count
FROM recordings
GROUP BY date
ORDER BY date DESC
LIMIT 10;
```
