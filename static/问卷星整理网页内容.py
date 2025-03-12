from bs4 import BeautifulSoup
from lxml import etree
import os

with open('1.txt', encoding='utf-8')as f1:
    html_doc = f1.read()

fileoutput = open('1output.txt', 'r+', encoding='utf-8')
alreadyhavetxt = fileoutput.read()

soup = BeautifulSoup(html_doc, 'html.parser')
tree = etree.HTML(html_doc)

elements = tree.xpath('//div[@class="data__items"]')

# 遍历每个元素并提取内容
for element in elements:
    # 提取问题和选项
    question = element.xpath('.//div[@class="data__tit_cjd"]/text()')[0].strip() if element.xpath('.//div[@class="data__tit_cjd"]/text()') else 'No question found'
    options = element.xpath('.//div[@class="ulradiocheck"]/div/span/text()')
    correct_answer = element.xpath('.//div[@class="answer-ansys"]/div/text()')[0].strip() if element.xpath('.//div[@class="answer-ansys"]/div/text()') else 'No correct answer found'

    # 输出提取的内容
    if question not in alreadyhavetxt:
        fileoutput.write('$' + question +'\n')
        for option in options:
            if option == '对':   option = 'A.对'
            elif option == '错': option = 'B.错'
            fileoutput.write(option+'\n')
        if correct_answer == '答案:对':    correct_answer = '答案:A.对'
        elif correct_answer == '答案:错':  correct_answer = '答案:B.错'
        fileoutput.write("答案:" + correct_answer + '\n')

fileoutput.close()


# 文件路径
file_path = '1output.txt'
# 获取文件大小（以字节为单位）
file_size = os.path.getsize(file_path)
# 输出文件大小
print(f"文件 '{file_path}' 的大小为: {file_size} 字节")