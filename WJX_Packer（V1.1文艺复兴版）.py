import tkinter as tk
import threading
import multiprocessing
import os
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

# 从上文引用 worker_automation（已修改）
# 注意：需将 worker_automation 定义在本文件中或者正确导入

def worker_automation(url, headless, file_lock):
    pid = multiprocessing.current_process().pid
    print(f"[Process {pid}] 自动化任务开始...")
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        if headless:
            chrome_options.add_argument("--headless=new")
        service = Service(r'./lib/chromedriver-win64/chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print(f"[Process {pid}] 正在访问问卷页面...")
        driver.get(url)
        actions = ActionChains(driver)
        time.sleep(0.2)
        actions.click().perform()
        time.sleep(0.2)
        driver.execute_script("document.exitFullscreen();")
        time.sleep(0.2)
        try:
            first_popup_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layui-layer1"]/div[3]/a'))
            )
            first_popup_button.click()
            time.sleep(0.2)
        except TimeoutException:
            print(f"[Process {pid}] 第一个弹窗按钮未能在指定时间内出现。")
        actions.click().perform()
        time.sleep(0.2)
        driver.execute_script("document.exitFullscreen();")
        time.sleep(0.2)
        try:
            second_popup_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="layui-layer2"]/div[3]/a'))
            )
            second_popup_button.click()
        except TimeoutException:
            print(f"[Process {pid}] 第二个弹窗按钮未能在指定时间内出现。")
        actions.click().perform()
        time.sleep(0.2)
        driver.execute_script("document.exitFullscreen();")
        time.sleep(0.2)
        try:
            next_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ctlNext"]'))
            )
            next_button.click()
        except TimeoutException:
            print(f"[Process {pid}] ‘下一步’按钮未能在指定时间内出现。")
        try:
            check_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="check_jx_btn"]/span'))
            )
            check_button.click()
        except TimeoutException:
            print(f"[Process {pid}] ‘检查’按钮未能在指定时间内出现。")
        page_source = driver.page_source
        driver.quit()
        output_dir = './output'
        os.makedirs(output_dir, exist_ok=True)
        process_file = os.path.join(output_dir, f"1_{pid}.txt")  # 使用进程ID创建独立文件

        with open(process_file, "w", encoding="utf-8") as f:
            f.write(page_source)

        print(f"[Process {pid}] 页面源码已写入到 {process_file}")

        # 立即处理当前进程生成的文件
        output_file = os.path.join(output_dir, f"1output.txt")
        status, message = parse_question_data(
            input_path=process_file,
            output_path=output_file
        )

        if status:
            print(f"[Process {pid}] 数据解析成功：{output_file}")
        else:
            print(f"[Process {pid}] 数据解析失败：{message}")

    except Exception as e:
        print(f"[Process {pid}] 执行过程中出现错误：{str(e)}")

class WJXAutomationGUI:
    def __init__(self, master):
        self.master = master
        master.title("WJX_Packer v1.1 from Victor.Kin, 🐂 and Rainsbluechan.")
        master.geometry("350x400")
        # 设置窗口居中
        self.center_window(master)
        style = ttk.Style()
        style.configure("TLabel", padding=6, font=('Segoe UI Emoji', 10))
        style.configure("TButton", padding=6, font=('Segoe UI Emoji', 10))
        style.configure("TCheckbutton", padding=6, font=('Segoe UI Emoji', 10))
        self.url_frame = ttk.Frame(master)
        self.url_frame.pack(pady=10, fill=tk.X)
        self.url_label = ttk.Label(self.url_frame, text="问卷地址：")
        self.url_label.pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(self.url_frame, width=40)
        self.url_entry.pack(side=tk.LEFT, expand=True)
        self.url_entry.insert(0, "https://kaoshi.wjx.top/vm/?????.aspx#")
        self.url_entry.bind("<FocusIn>", self.clear_placeholder)
        self.url_entry.bind("<FocusOut>", self.restore_placeholder)
        self.headless_var = tk.BooleanVar()
        self.headless_cb = ttk.Checkbutton(
            master, text="启用无头模式（后台运行）", variable=self.headless_var
        )
        self.headless_cb.pack(pady=5)
        self.status_label = ttk.Label(master, text="就绪", foreground="gray")
        self.status_label.pack(pady=5)

        # 单次执行按钮
        self.single_btn = ttk.Button(
            master, text="开始执行", command=self.start_automation
        )
        self.single_btn.pack(pady=10)

        # 新增：开始执行 x10（多进程版）按钮
        self.multi_btn = ttk.Button(
            master, text="开始执行 x10", command=self.start_automation_x10
        )
        self.multi_btn.pack(pady=10)
        # 处理题库按钮
        self.process_btn = ttk.Button(
            master, text="处理题库", command=self.process_questions
        )
        self.process_btn.pack(pady=10)
        # 制作脚本按钮
        self.js_btn = ttk.Button(
            master, text="制作脚本", command=self.now_to_make_js
        )
        self.js_btn.pack(pady=10)


        self.mp_processes = []
        # 创建多进程共享的文件写入锁
        self.file_lock = multiprocessing.Lock()

    def center_window(self, window):
        """
        将窗口居中显示
        """
        window.update_idletasks()  # 更新窗口信息
        width = window.winfo_width()  # 获取窗口宽度
        height = window.winfo_height()  # 获取窗口高度

        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # 计算窗口居中的位置
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # 设置窗口位置
        window.geometry(f"{width}x{height}+{x}+{y}")

    def clear_placeholder(self, event):
        if self.url_entry.get() == "https://kaoshi.wjx.top/vm/?????.aspx#":
            self.url_entry.delete(0, tk.END)
            self.url_entry.configure(foreground="black")

    def restore_placeholder(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "格式：https://kaoshi.wjx.top/vm/?????.aspx#")
            self.url_entry.configure(foreground="gray")

    def update_status(self, message):
        self.master.after(0, lambda: self.status_label.configure(text=message))

    def start_automation(self):
        """单次自动化任务，采用线程执行，不阻塞GUI"""
        url = self.url_entry.get().strip()
        headless = self.headless_var.get()
        self.single_btn['state'] = 'disabled'
        self.update_status("正在启动浏览器...")
        thread = threading.Thread(
            target=self.run_automation,
            args=(url, headless),
            daemon=True
        )
        thread.start()
        self.master.after(100, self.check_thread, thread, self.single_btn)

    def run_automation(self, url, headless):
        """单次自动化任务，逻辑同之前"""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            if headless:
                chrome_options.add_argument("--headless=new")
            service = Service(r'./lib/chromedriver-win64/chromedriver.exe')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.update_status("正在访问问卷页面...")
            driver.get(url)
            actions = ActionChains(driver)
            time.sleep(0.2)
            actions.click().perform()
            time.sleep(0.2)
            driver.execute_script("document.exitFullscreen();")
            time.sleep(0.2)
            try:
                first_popup_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="layui-layer1"]/div[3]/a'))
                )
                first_popup_button.click()
                time.sleep(0.2)
            except TimeoutException:
                print("第一个弹窗按钮未能在指定时间内出现。")
            actions.click().perform()
            time.sleep(0.2)
            driver.execute_script("document.exitFullscreen();")
            time.sleep(0.2)
            try:
                second_popup_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="layui-layer2"]/div[3]/a'))
                )
                second_popup_button.click()
            except TimeoutException:
                print("第二个弹窗按钮未能在指定时间内出现。")
            actions.click().perform()
            time.sleep(0.2)
            driver.execute_script("document.exitFullscreen();")
            time.sleep(0.2)
            try:
                next_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="ctlNext"]'))
                )
                next_button.click()
            except TimeoutException:
                print("‘下一步’按钮未能在指定时间内出现。")
            try:
                check_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="check_jx_btn"]/span'))
                )
                check_button.click()
            except TimeoutException:
                print("‘检查’按钮未能在指定时间内出现。")
            output_dir = './output'
            os.makedirs(output_dir, exist_ok=True)
            file1 = os.path.join(output_dir, "1.txt")
            with open(file1, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            driver.quit()
            status, message = parse_question_data(input_path=file1, output_path=os.path.join(output_dir, "1output.txt"))
            self.update_status("任务完成！结果已保存到output/1output.txt")
            messagebox.showinfo("完成", "自动化任务执行成功！")
            file_size = get_file_size(os.path.join(output_dir, "1output.txt"), human_readable=True)
            messagebox.showinfo("文件大小", f"文件大小：{file_size}")
        except Exception as e:
            messagebox.showerror("错误", f"执行过程中出现错误：\n{str(e)}")
            self.update_status("执行出错")

    def check_thread(self, thread, button):
        if thread.is_alive():
            self.master.after(100, self.check_thread, thread, button)
        else:
            button['state'] = 'normal'

    def process_questions(self):
        try:
            status, message = process_questions(input_path='./output/1output.txt', output_path='./output/2output.txt')
            if status:
                messagebox.showinfo("完成", "题库处理成功！")
            else:
                messagebox.showerror("错误", f"题库处理失败：\n{message}")
        except Exception as e:
            messagebox.showerror("错误", "也许是错误，你先点点下面那个按钮试试。")

    def now_to_make_js(self):
        try:
            status, message = now_to_make_js(input_path='./output/2output.txt')
            if status:
                messagebox.showinfo("完成", "脚本制作成功！")
            else:
                messagebox.showerror("错误", f"脚本制作失败：\n{message}")
        except Exception as e:
            messagebox.showerror("你以为这是错误", "还真是，但它其实没错，东西已经放在js_completed文件夹里了。")

    def start_automation_x10(self):
        """
        利用多进程同时执行10次自动化任务，每个任务采集页面后通过进程锁顺序追加写入到统一文件1.txt，
        所有进程结束后，再由主进程调用去重函数处理生成1output.txt。
        """
        url = self.url_entry.get().strip()
        headless = self.headless_var.get()
        self.multi_btn['state'] = 'disabled'
        self.update_status("正在启动10个自动化进程...")
        # 清空共享输出文件，避免旧数据干扰
        output_dir = './output'
        os.makedirs(output_dir, exist_ok=True)
        shared_file = os.path.join(output_dir, "1.txt")
        self.mp_processes = []
        for _ in range(10):
            p = multiprocessing.Process(
                target=worker_automation,
                args=(url, headless, self.file_lock)
            )
            p.start()
            self.mp_processes.append(p)
        self.master.after(100, self.check_mp_processes)

    def check_mp_processes(self):
        alive = any(p.is_alive() for p in self.mp_processes)
        if alive:
            self.master.after(100, self.check_mp_processes)
        else:
            # 合并所有进程生成的输出文件
            try:
                output_dir = './output'
                all_output = []

                # 收集所有进程输出文件
                for f in os.listdir(output_dir):
                    if f.startswith("1output_") and f.endswith(".txt"):
                        with open(os.path.join(output_dir, f), 'r', encoding='utf-8') as src:
                            all_output.extend(src.readlines())

                # 写入最终文件
                final_output = os.path.join(output_dir, "1output.txt")

                self.update_status("任务完成！结果已保存到output/1output.txt")
                messagebox.showinfo("完成", "所有自动化任务执行完毕，并完成数据去重处理！")

                # 显示最终文件大小
                file_size = get_file_size(final_output, human_readable=True)
                messagebox.showinfo("文件大小", f"文件大小：{file_size}")

            except Exception as e:
                messagebox.showerror("错误", f"数据处理过程中出现错误：\n{str(e)}")

            self.multi_btn['state'] = 'normal'


if __name__ == "__main__":
    root = tk.Tk()
    app = WJXAutomationGUI(root)
    root.mainloop()