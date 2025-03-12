import re
import pandas as pd

questions = []
tigan = []
text2 = ''
m = -1
# 读取txt文件
with open("./2.txt", encoding='utf-8') as f1:
    text = f1.readlines()
    for line in text:
        if '$' in line:
            m += 1
            questions.append([])
        questions[m].append(line)
    answers = ['【答案】']*len(questions)
    for i in range(len(questions)):
        tigan.append(questions[i][0].replace("\n", "").replace("【多选题】", ""))
        if 'A' in questions[i][-1]:
            answers[i] += questions[i][1].replace("\n", "")
        if 'B' in questions[i][-1]:
            answers[i] += questions[i][2].replace("\n", "")
        if 'C' in questions[i][-1]:
            answers[i] += questions[i][3].replace("\n", "")
        if 'D' in questions[i][-1]:
            answers[i] += questions[i][4].replace("\n", "")
        if '对' in questions[i][-1]:
            answers[i] += questions[i][1].replace("\n", "")
        if '错' in questions[i][-1]:
            answers[i] += questions[i][2].replace("\n", "")
        text2 = ''.join(text2 + tigan[i] + answers[i])

text3 = re.sub("[ |\n|\t|《|》|（|）|(|)|,|，| |/|。|、|...|？|?|\-|’|\[|\]|‘|“|”|；|！|：|:|\"|>|<|…|;|.|．]", '', text2).strip()

with open("2output.txt", "w", encoding='utf-8') as f2:
    f2.write(text3)