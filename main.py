import tkinter as tk
from tkinter import filedialog, messagebox
import concurrent.futures
import requests

def translate_text_with_deepl(text, target_language='ZH', auth_key='1c9b9545-c3ac-7d1e-1fa5-aca070eb189d:fx'):
    url = "https://api-free.deepl.com/v2/translate"
    data = {
        'auth_key': auth_key,
        'text': text,
        'target_lang': target_language
    }
    response = requests.post(url, data=data)
    return response.json()['translations'][0]['text']

def parse_srt(srt_content):
    entries = []
    current_entry = []
    lines = srt_content.split('\n')

    for line in lines:
        if line.strip():
            current_entry.append(line)
        else:
            if current_entry:
                sequence_number = current_entry[0]
                timestamp = current_entry[1]
                text = ' '.join(current_entry[2:])
                entries.append((sequence_number, timestamp, text))
                current_entry = []

    # 处理可能的最后一个条目
    if current_entry:
        sequence_number = current_entry[0]
        timestamp = current_entry[1]
        text = ' '.join(current_entry[2:])
        entries.append((sequence_number, timestamp, text))

    return entries

def generate_new_srt(translated_entries):
    new_srt_content = ''
    for entry in translated_entries:
        new_srt_content += f"{entry[0]}\n{entry[1]}\n{entry[2]}\n\n"
    return new_srt_content

# 读取原始字幕文件
with open('/Users/loyo/PycharmProjects/TranslateSubtitles/src/2022_lecture1_720p_sdr-en.srt', 'r', encoding='utf-8') as file:
    original_srt_content = file.read()


# 解析字幕文件
parsed_entries = parse_srt(original_srt_content)

# 翻译字幕
translated_entries = []
total_entries = len(parsed_entries)

def translate_entry(entry):
    return (entry[0], entry[1], translate_text_with_deepl(entry[2]))

# 使用 ThreadPoolExecutor 并行处理翻译
with concurrent.futures.ThreadPoolExecutor() as executor:
    for index, result in enumerate(executor.map(translate_entry, parsed_entries)):
        translated_entries.append(result)
        print(f"Progress: {index + 1}/{total_entries} entries translated")

# 生成新的字幕文件
new_srt_content = generate_new_srt(translated_entries)

# 保存翻译后的字幕文件
with open('path_to_translated_srt_file.srt', 'w', encoding='utf-8') as file:
    file.write(new_srt_content)
