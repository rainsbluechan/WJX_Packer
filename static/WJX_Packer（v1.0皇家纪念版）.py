import tkinter as tk
import os
import threading
import re
import multiprocessing
import time
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from func import (
    parse_question_data,
    get_file_size,
    process_questions,
    now_to_make_js
)


class WJXAutomationGUI:
    def __init__(self, master):
        self.master = master
        master.title("WJX_Packer v1.0 from Victor.Kin, 🐂 and Rainsbluechan.")

        master.geometry("600x400")

        # 样式配置
        style = ttk.Style()
        style.configure("TLabel", padding=6, font=('Segoe UI Emoji', 10))
        style.configure("TButton", padding=6, font=('Segoe UI Emoji', 10))
        style.configure("TCheckbutton", padding=6, font=('Segoe UI Emoji', 10))

        # URL输入框
        self.url_frame = ttk.Frame(master)
        self.url_frame.pack(pady=10, fill=tk.X)

        self.url_label = ttk.Label(self.url_frame, text="问卷地址：")
        self.url_label.pack(side=tk.LEFT)

        self.url_entry = ttk.Entry(self.url_frame, width=40)
        self.url_entry.pack(side=tk.LEFT, expand=True)
        self.url_entry.insert(0, "https://kaoshi.wjx.top/vm/?????.aspx#")
        self.url_entry.bind("<FocusIn>", self.clear_placeholder)
        self.url_entry.bind("<FocusOut>", self.restore_placeholder)

        # 无头模式复选框
        self.headless_var = tk.BooleanVar()
        self.headless_cb = ttk.Checkbutton(
            master,
            text="启用无头模式（后台运行）",
            variable=self.headless_var
        )
        self.headless_cb.pack(pady=5)

        # 状态标签
        self.status_label = ttk.Label(master, text="就绪", foreground="gray")
        self.status_label.pack(pady=5)

        # 开始按钮
        self.start_btn = ttk.Button(
            master,
            text="开始执行",
            command=self.start_automation
        )
        self.start_btn.pack(pady=10)

        self.start_btn = ttk.Button(
            master,
            text="处理题库",
            command=self.process_questions
        )
        self.start_btn.pack(pady=10)

        self.start_btn = ttk.Button(
            master,
            text="制作脚本",
            command=self.now_to_make_js
        )
        self.start_btn.pack(pady=10)

    def clear_placeholder(self, event):
        """清空输入框提示文字"""
        if self.url_entry.get() == "https://kaoshi.wjx.top/vm/?????.aspx#":
            self.url_entry.delete(0, tk.END)
            self.url_entry.configure(foreground="black")

    def restore_placeholder(self, event):
        """恢复输入框提示文字"""
        if not self.url_entry.get():
            self.url_entry.insert(0, "格式：https://kaoshi.wjx.top/vm/?????.aspx#")
            self.url_entry.configure(foreground="gray")

    def run_automation(self, url, headless):
        """执行自动化任务"""
        try:
            # 配置Chrome选项
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            if headless:
                chrome_options.add_argument("--headless=new")

            # 初始化浏览器
            service = Service(r'./lib/chromedriver-win64/chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # 更新状态
            self.update_status("正在访问问卷页面...")
            driver.get(url)

            # 后续自动化操作...
            actions = ActionChains(driver)
            time.sleep(0.2)

            # 第一次操作
            actions.click().perform()
            time.sleep(0.2)
            driver.execute_script("document.exitFullscreen();")
            time.sleep(0.2)

            # 等待第一个弹窗出现并可点击
            try:
                first_popup_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="layui-layer1"]/div[3]/a'))
                )
                first_popup_button.click()
                time.sleep(0.2)  # 等待弹窗消失
            except TimeoutException:
                print("第一个弹窗按钮未能在指定时间内出现。")

            # 再次左键点击以进入全屏
            actions.click().perform()
            time.sleep(0.2)  # 等待全屏效果

            # 使用JavaScript退出全屏
            driver.execute_script("document.exitFullscreen();")
            time.sleep(0.2)  # 等待退出全屏

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
            time.sleep(0.2)  # 等待全屏效果

            # 使用JavaScript退出全屏
            driver.execute_script("document.exitFullscreen();")
            time.sleep(0.2)  # 等待退出全屏

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

            # 保存结果
            page_source = driver.page_source
            with open('./output/1.txt', 'w', encoding='utf-8') as f:
                f.write(page_source)

            driver.quit()
            # 解析并保存题库到1output.txt
            status, message = parse_question_data(input_path='./output/1.txt', output_path='./output/1output.txt')
            self.update_status("任务完成！结果已保存到output/1output.txt")
            messagebox.showinfo("完成", "自动化任务执行成功！")
            file_size = get_file_size('./output/1output.txt', human_readable=True)
            messagebox.showinfo("文件大小", f"文件大小：{file_size}")

        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出现错误：\n{str(e)}")
            self.update_status("执行出错")

    def update_status(self, message):
        """更新状态标签"""
        self.master.after(0, lambda: self.status_label.configure(text=message))

    def start_automation(self):
        """启动自动化线程"""
        url = self.url_entry.get().strip()
        # 获取无头模式状态
        headless = self.headless_var.get()

        # 禁用开始按钮
        self.start_btn['state'] = 'disabled'
        self.update_status("正在启动浏览器...")

        # 在独立线程中运行自动化
        thread = threading.Thread(
            target=self.run_automation,
            args=(url, headless),
            daemon=True
        )
        thread.start()

        # 启用按钮监控
        self.master.after(100, self.check_thread, thread)

    def check_thread(self, thread):
        """监控线程状态"""
        if thread.is_alive():
            self.master.after(100, self.check_thread, thread)
        else:
            self.start_btn['state'] = 'normal'

    def process_questions(self):
        """处理题库"""
        try:
            status, message = process_questions(input_path='./output/1output.txt', output_path='./output/2output.txt')
            if status:
                messagebox.showinfo("完成", "题库处理成功！")
            else:
                messagebox.showerror("错误", f"题库处理失败：\n{message}")

        except Exception as e:
            messagebox.showerror("没事", f"已经好了，你不用理我")

    def now_to_make_js(self):
        """制作脚本"""
        try:
            status, message = now_to_make_js(input_path='./output/2output.txt')
            if status:
                messagebox.showinfo("完成", "脚本制作成功！")
            else:
                messagebox.showerror("错误", f"脚本制作失败：\n{message}")

        except Exception as e:
            messagebox.showerror("没事", f"已经好了，你不用理我，东西我放在js_completed文件夹里了\n{str('可前往浏览器进行f12调试')}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WJXAutomationGUI(root)
    root.mainloop()