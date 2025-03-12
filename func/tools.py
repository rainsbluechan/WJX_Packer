# tools.py
import os
import re
import shutil
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree

def parse_question_data(input_path='./output/1.txt', output_path='./output/1output.txt'):
    """
    解析问卷星结果文件并生成格式化题库
    参数：
        input_path: 输入文件路径（默认：1.txt）
        output_path: 输出文件路径（默认：1output.txt）
    返回：
        tuple: (处理状态, 输出文件大小) 或 (False, 错误信息)
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 读取输入文件
        with open(input_path, 'r', encoding='utf-8') as f:
            html_doc = f.read()

        # 读取已有输出内容
        existing_content = ''
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()

        # 解析HTML
        tree = etree.HTML(html_doc)
        elements = tree.xpath('//div[@class="data__items"]')

        # 写入新内容
        new_questions = 0
        with open(output_path, 'a', encoding='utf-8') as output_file:
            for element in elements:
                # 提取问题
                question = element.xpath('.//div[@class="data__tit_cjd"]/text()')
                question = question[0].strip() if question else '未找到问题'

                # 跳过已存在的问题
                if question in existing_content:
                    continue

                # 提取选项
                options = element.xpath('.//div[@class="ulradiocheck"]/div/span/text()')

                # 提取正确答案
                correct_answer = element.xpath('.//div[@class="answer-ansys"]/div/text()')
                correct_answer = correct_answer[0].strip() if correct_answer else '未找到答案'

                # 写入问题
                output_file.write(f'${question}\n')

                # 处理并写入选项
                for option in options:
                    if option == '对':
                        processed = 'A.对'
                    elif option == '错':
                        processed = 'B.错'
                    else:
                        processed = option  # 保持原样不添加序号
                    output_file.write(f"{processed}\n")

                # 处理并写入答案
                if correct_answer == '对':
                    ans = 'A.对'
                elif correct_answer == '错':
                    ans = 'B.错'
                else:
                    ans = correct_answer
                output_file.write(f"答案:{ans}\n")  # 保持单换行

                new_questions += 1

        # 获取文件信息
        file_size = os.path.getsize(output_path)
        return (True, f"成功添加 {new_questions} 道新题，当前文件大小：{file_size} 字节")

    except FileNotFoundError:
        return (False, f"输入文件 {input_path} 不存在")
    except Exception as e:
        return (False, f"解析失败：{str(e)}")

def get_file_size(file_path, human_readable=False):
    """
    获取文件大小
    参数：
        file_path: 文件路径（字符串）
        human_readable: 是否返回人类可读格式（如 KB/MB）
    返回：
        int 或 str: 文件大小（字节或人类可读格式），如果文件不存在则返回 -1
    """
    try:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if human_readable:
                # 转换为人类可读格式
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024:
                        return f"{size:.2f} {unit}"
                    size /= 1024
                return f"{size:.2f} TB"
            else:
                return size
        else:
            return -1
    except Exception as e:
        print(f"获取文件大小失败：{str(e)}")
        return -1

def process_questions(input_path="./1output.txt", output_path="./2output.txt"):
    """
    处理问卷文件并生成格式化文本
    参数：
        input_path: 输入文件路径（默认：./1output.txt）
        output_path: 输出文件路径（默认：./2output.txt）
    """
    questions = []
    tigan = []
    text2 = ''
    m = -1

    # 读取处理文件
    with open(input_path, encoding='utf-8') as f1:
        text = f1.readlines()
        for line in text:
            if '$' in line:
                m += 1
                questions.append([])  # 新建一个空列表
            if m >= len(questions):
                questions.append([])  # 防止越界
            questions[m].append(line)

        # 生成答案列表
        answers = ['【答案】'] * len(questions)

        # 处理每个问题
        for i in range(len(questions)):
            # 提取题干
            tigan.append(questions[i][0].replace("\n", "").replace("【多选题】", ""))

            # 原始答案处理逻辑
            last_line = questions[i][-1].replace("\n", "")
            if 'A' in last_line:
                answers[i] += questions[i][1].replace("\n", "")
            if 'B' in last_line:
                answers[i] += questions[i][2].replace("\n", "")
            if 'C' in last_line:
                answers[i] += questions[i][3].replace("\n", "")
            if 'D' in last_line:
                answers[i] += questions[i][4].replace("\n", "")
            if '对' in last_line:
                answers[i] += questions[i][1].replace("\n", "")
            if '错' in last_line:
                answers[i] += questions[i][2].replace("\n", "")

            # 拼接结果
            text2 += tigan[i] + answers[i]

    # 正则过滤特殊字符
    text3 = re.sub(
        r'[ \n\t《》()（）,， /。、…？?\-’‘“”\[\]；！:："«»><>;\.．]',
        '',
        text2
    ).strip()

    # 写入输出文件
    with open(output_path, "w", encoding='utf-8') as f2:
        f2.write(text3)

    return text3  # 返回处理结果

def now_to_make_js(input_path='./2output.txt'):
    """
    将处理后的文本注入JS模板并生成带时间戳的备份
    返回：(状态, 消息)
    """
    with open(input_path, 'r', encoding='utf-8') as file:
        original_str = file.read()
        original_str = original_str.replace('答案:', '【答案】')
    # 匹配并替换数字、标点符号和空格
    clean_str = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9【】$]', '', original_str)
    # 剔除空格
    clean_str = clean_str.replace(' ', '')
    # 获取当前年份和月份
    current_time = datetime.datetime.now()
    file_name = f"{current_time.year}_{current_time.month}.txt"

    # 生成要写入的内容
    content = f"""var questions = document.querySelectorAll(".field-label");
    for (var i = 0; i < questions.length; i++) {{
        var question = questions[i];
        var questionText = question.textContent.trim();
        var filteredText = questionText.replace(/[^\\u4e00-\\u9fa50-9]/g, '');  
        filteredText = filteredText.replace(/^\d{{1,6}}/, '');
        filteredText = filteredText.replace(/单选题/g, '')
        filteredText = filteredText.replace(/多选题/g, '')
        filteredText = filteredText.replace(/判断题/g, '')
        var question_bank = '{clean_str}';  // 将 original_str 放入这里

        var daan = '';
        var p_end = 0;
        while (true) {{

            var p = question_bank.indexOf(filteredText, p_end);
            if (p === -1) {{
                break;
            }} else {{
                var end = question_bank.indexOf("【答案】", p);
                if (end === -1) {{
                    p_end += 1;
                }} else {{
                    p_end = end;
                    var p_next = question_bank.indexOf("$", p);
                    if (p_next !== -1) {{
                        daan += question_bank.slice(p_end + 4, p_next);
                        daan += "···";
                    }} else {{
                        daan += question_bank.substring(p_end + 4);
                        daan += "···";
                    }}
                }}
            }}
        }}
        if (daan === '') {{
            daan += "题库未收录";
        }}
        question.textContent += daan;
    }}"""

    # 将内容写入文件
    with open(f"./js_completed/{file_name}", 'w', encoding='utf-8') as file:
        file.write(content)

