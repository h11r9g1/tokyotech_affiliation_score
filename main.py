import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np


# userID, password
MY_STUDENT_NUMBER = 'your student number'
MY_PASSWORD = 'your password'
# [A,1] -> [B,1] -> [C,1] -> ... -> [J,1] -> [A,2] -> [B,2] -> ...
# example
# matrix_code = 'abcdefghij' \
#               'abcdefghij' \
#               'abcdefghij' \
#               'abcdefghij' \
#               'abcdefghij' \
#               'abcdefghij' \
#               'abcdefghij'
matrix_code = 'your matrix'

assert(len(matrix_code) == 70)

for i in range(7):

    if i == 0:
        MATRIX_CODE = [c for c in matrix_code[:10]]
    else:
        MATRIX_CODE = np.vstack([MATRIX_CODE, [c for c in matrix_code[:10]]])

    matrix_code = matrix_code[10:]


# TokyoTechPortal login
LoginURL1 = 'https://portal.nap.gsic.titech.ac.jp/GetAccess/' \
            'Login?Template=userpass_key&AUTHMETHOD=UserPassword'

driver_path = ChromeDriverManager().install()
driver = webdriver.Chrome(service=Service(executable_path=driver_path))

driver.get(LoginURL1)
time.sleep(1)

account = driver.find_element(By.NAME, 'usr_name')
password = driver.find_element(By.NAME, 'usr_password')
login = driver.find_element(By.NAME, 'OK')

account.clear()
password.clear()

account.send_keys(MY_STUDENT_NUMBER)
password.send_keys(MY_PASSWORD)
login.click()


# Matrix Assignment
time.sleep(1)
LoginURL2 = driver.current_url

res = requests.get(LoginURL2)
soup = BeautifulSoup(res.text, "lxml")
matrix1 = driver.find_element(By.CSS_SELECTOR, '#authentication > tbody > tr:nth-child(5) > th:nth-child(1)')
matrix2 = driver.find_element(By.CSS_SELECTOR, '#authentication > tbody > tr:nth-child(6) > th:nth-child(1)')
matrix3 = driver.find_element(By.CSS_SELECTOR, '#authentication > tbody > tr:nth-child(7) > th:nth-child(1)')
del soup

row1 = int(matrix1.text[3])-1
column1 = ord(matrix1.text[1])-65
row2 = int(matrix2.text[3])-1
column2 = ord(matrix2.text[1])-65
row3 = int(matrix3.text[3])-1
column3 = ord(matrix3.text[1])-65

login = driver.find_element(By.NAME, 'OK')

mat_code1 = driver.find_element(By.NAME, 'message3')
mat_code2 = driver.find_element(By.NAME, 'message4')
mat_code3 = driver.find_element(By.NAME, 'message5')

mat_code1.clear()
mat_code2.clear()
mat_code3.clear()

mat_code1.send_keys(MATRIX_CODE[row1][column1])
mat_code2.send_keys(MATRIX_CODE[row2][column2])
mat_code3.send_keys(MATRIX_CODE[row3][column3])

login.click()
time.sleep(2)


# Web system for Student and Faculty
SandFWeb = driver.find_element(By.CSS_SELECTOR, 'body > center > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td.resource > table > tbody > tr:nth-child(1) > td:nth-child(2) > a')
driver.get(SandFWeb.get_attribute('href'))
time.sleep(3)


# get list of grades
Grades = driver.find_element(By.CSS_SELECTOR, '#ctl00_ContentPlaceHolder1_HyperLink39')
Grades_url = Grades.get_attribute('href')
driver.get(Grades_url)
del Grades
time.sleep(2)

soup = BeautifulSoup(driver.page_source, 'lxml')
table = soup.find_all('table')
dfs = pd.read_html(str(table))
dfs = dfs[9:14]

for i in range(len(dfs)):
    df = dfs[i]
    if not i:
        grade_list = dfs[i]
    else:
        grade_list = pd.concat([grade_list, dfs[i]], ignore_index=True)

# grade_list [ ('subject_name', 'grade', credit) ]
grade_list = grade_list.iloc[:, [2, 5, 6]]
grade_list = grade_list.rename(columns={'授業科目名 ▼/▲': '授業科目名', '成績 ▼/▲': '成績'})


# classify as compulsory or elective_sub
cmp = ['線形代数学第一・演習', '力学基礎１', '電磁気学基礎１', '心理学Ａ',
       '英語第一', '外国語への招待１', '有機化学基礎', '生命科学基礎第一２', '技術史Ａ',
       '化学熱力学基礎', '力学基礎２', '英語第二', '生命科学基礎第一１', '電磁気学基礎２',
       '微分積分学第一・演習', '無機化学基礎', '英語第三', '量子化学基礎', '文化人類学Ａ',
       '歴史学Ａ', 'コミュニケーション論Ａ', '教養特論：多文化共生論', '外国語への招待１',
       '法学（民事法）Ａ', '国際関係論Ａ', '社会学Ａ', '科学技術社会論・科学技術政策Ａ',
       '意思決定論Ａ', '学びのデザイン', '教養特論：ミュージアムから学ぶ科学・技術・文化コミュニケーション',
       '未来社会論Ａ', '英語圏文化を知る', '教養特論:経営学入門', '教養特論:経済学入門',
       '考古学・自然人類学Ａ', '芸術Ａ', '文化人類学Ａ', '教養特論:言語と文化',
       '外国語への招待２', '法学(憲法)Ａ', '国際関係論Ａ', '教養特論:現代社会の課題とコミュニケーション',
       '経済学Ａ', '教養特論:障害学', '統計学Ａ', '科学史Ａ', '科学技術倫理Ａ',
       '社会モデリングＡ', '教養特論:未来社会デザイン入門', '哲学Ａ', '文学Ａ', '宗教学Ａ',
       '表象文化論Ａ', '政治学Ａ', '教養特論:ファッション論', 'メディア論Ａ',
       '教養特論:東南アジア', '教養特論:アメリカ学', '技術史Ａ', '科学哲学Ａ',
       '言語学Ａ', '教養特論:技術と美術の哲学', '未来社会論Ａ', '教養特論:スポーツ科学'
       ]

compulsory_sub = []
elective_sub = []

for i in range(len(grade_list)):
    if grade_list.iloc[i]['成績'] == '-':
        continue
    c = grade_list.iloc[i]['単位'].split('-')
    cr = int(float(c[0]) + float(c[1]) + float(c[2]))
    grade_list.iloc[i]['単位'] = cr
    if grade_list.iloc[i]['授業科目名'] in cmp:
        compulsory_sub.append(
            (grade_list.iloc[i]['授業科目名'], grade_list.iloc[i]['成績'], grade_list.iloc[i]['単位'])
        )
    else:
        elective_sub.append(
            (grade_list.iloc[i]['授業科目名'], grade_list.iloc[i]['成績'], grade_list.iloc[i]['単位'])
        )


score = 0
subject_grade = []
GPA = 0
GPT = 0


grades = [(r[1], r[2]) for r in compulsory_sub + elective_sub]
crdits = 0
average = 0

for i, grade in enumerate(grades):
    if grade[0] == '合格':
        grades.pop(i)
    else:
        crdits += grade[1]

for grade, crdit in grades:
    if int(grade) >= 60:
        GPA += (int(grade) - 55) * crdit
        average += int(grade)

GPT = GPA / 1100
GPA /= (crdits * 10)
print('平均点：', format(average / len(grades), '.2f'))
print('GPA：', format(GPA, '.2f'))
print('GPT：', format(GPT, '.2f'))


# even out credit weight
def reflect_credits(_sub_list: list[(str, str, int)]) -> list:
    _new_list = []
    for _subject, _grade, _crd in _sub_list:
        if _grade == '合格':
            continue
        for _ in range(_crd):
            _new_list.append((_subject, int(_grade)))
    return _new_list


compulsory_list = reflect_credits(compulsory_sub)
elective_list = reflect_credits(elective_sub)


# calculate affiliation score
compulsory_list = sorted(compulsory_list, reverse=True, key=lambda x: x[1])

for _ in range(17):
    score += compulsory_list[0][1]
    subject_grade.append(compulsory_list[0])
    compulsory_list.pop(0)

compulsory_list = compulsory_list + elective_list
compulsory_list = sorted(compulsory_list, reverse=True, key=lambda x: x[1])

for _ in range(14):
    score += compulsory_list[0][1]
    subject_grade.append(compulsory_list[0])
    compulsory_list.pop(0)


# display affiliation score and subjects
subject_grade = sorted(subject_grade, reverse=True, key=lambda x: x[1])
print('系所属点：', score)

assert(len(subject_grade) == 31)

for i in range(31):
    subject, grade = subject_grade[i]
    print(subject, grade)
