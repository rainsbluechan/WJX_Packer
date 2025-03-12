from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # 修改为Chrome的Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException  # 添加TimeoutException导入
import time

# 设置Chrome浏览器选项
chrome_options = webdriver.ChromeOptions()
# 禁用自动化提示条（"Chrome正在受到自动测试软件的控制"）
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# 设置ChromeDriver路径（需要修改为你的chromedriver实际路径）
chrome_service = Service(r'./lib/chromedriver-win64/chromedriver.exe')  # 修改为chromedriver路径
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)  # 修改为Chrome驱动

# 打开指定的问卷星页面
driver.get('https://kaoshi.wjx.top/vm/OBbt1Sm.aspx#')

# 等待页面加载（建议改用显式等待）
time.sleep(1)

# 创建ActionChains对象
actions = ActionChains(driver)

# 第一次左键点击以进入全屏
actions.click().perform()
time.sleep(0.5)

# 使用JavaScript退出全屏（Chrome同样适用）
driver.execute_script("document.exitFullscreen();")
time.sleep(0.5)

# 等待第一个弹窗出现并可点击
try:
    first_popup_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="layui-layer1"]/div[3]/a'))
    )
    first_popup_button.click()
    time.sleep(0.5)  # 等待弹窗消失
except TimeoutException:
    print("第一个弹窗按钮未能在指定时间内出现。")

# 再次左键点击以进入全屏
actions.click().perform()
time.sleep(0.5)  # 等待全屏效果

# 使用JavaScript退出全屏
driver.execute_script("document.exitFullscreen();")
time.sleep(0.5)  # 等待退出全屏

# 等待第二个弹窗出现并可点击
try:
    second_popup_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="layui-layer2"]/div[3]/a'))
    )
    second_popup_button.click()
except TimeoutException:
    print("第二个弹窗按钮未能在指定时间内出现。")

# 第3次左键点击以进入全屏
actions.click().perform()
time.sleep(0.5)  # 等待全屏效果

# 使用JavaScript退出全屏
driver.execute_script("document.exitFullscreen();")
time.sleep(0.5)  # 等待退出全屏

# 等待并点击“下一步”按钮
try:
    next_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="ctlNext"]'))
    )
    next_button.click()
except TimeoutException:
    print("‘下一步’按钮未能在指定时间内出现。")

# 等待并点击“检查”按钮
try:
    check_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="check_jx_btn"]/span'))
    )
    check_button.click()
except TimeoutException:
    print("‘检查’按钮未能在指定时间内出现。")

# 获取最后跳转页面的源代码
page_source = driver.page_source

# 保存源代码到文件
with open('1.txt', 'w', encoding='utf-8') as file:
    file.write(page_source)

# 关闭浏览器
# driver.quit()