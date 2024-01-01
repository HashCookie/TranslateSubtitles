import requests
import concurrent.futures   # 导入 concurrent.futures 模块
import os


# 函数使用 DeepL API 翻译文本
def translate_text_with_deepl(text, target_language='ZH', auth_key='3688cca9-ad8f-2ab9-05ed-9a78de7aa541'):
    url = "https://api.deepl.com/v2/translate"
    data = {
        'auth_key': auth_key,
        'text': text,
        'target_lang': target_language
    }
    response = requests.post(url, data=data)
    return response.json()['translations'][0]['text']


# 函数解析 SRT 文件并返回一个列表，其中包含每个条目的元组
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


# 函数生成新的 SRT 文件内容
def generate_new_srt(translated_entries):
    new_srt_content = ''
    for entry in translated_entries:
        new_srt_content += f"{entry[0]}\n{entry[1]}\n{entry[2]}\n\n"
    return new_srt_content

# 读取原始字幕文件
input_file_path = '/Users/loyo/PycharmProjects/TranslateSubtitles/src/week4/2022_lecture4_720p_sdr-en.srt'
with open(input_file_path, 'r', encoding='utf-8') as file:
    original_srt_content = file.read()


# 解析字幕文件
parsed_entries = parse_srt(original_srt_content)

# 翻译字幕
translated_entries = []
total_entries = len(parsed_entries)


# 函数使用 DeepL API 翻译文本
def translate_entry(entry):
    return (entry[0], entry[1], translate_text_with_deepl(entry[2]))

# 使用 ThreadPoolExecutor 并行处理翻译
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  # 您可以根据需要调整 max_workers
    for index, result in enumerate(executor.map(translate_entry, parsed_entries)):
        translated_entries.append(result)
        print(f"Progress: {index + 1}/{total_entries} entries translated")


# 生成新的字幕文件
new_srt_content = generate_new_srt(translated_entries)

# 提取原始文件名并在其后添加 "_cn"
base_name = os.path.basename(input_file_path)
name, ext = os.path.splitext(base_name)
output_filename = name.replace("-en", "-cn") + ext

# 保存翻译后的字幕文件
with open(output_filename, 'w', encoding='utf-8') as file:
    file.write(new_srt_content)