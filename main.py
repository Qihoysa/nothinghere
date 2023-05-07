# This Python file uses the following encoding: utf-8
import tkinter as tk
from vits_pack import Vits
from aiui import XFServerAudio
from recording import recording

paimon = Vits()


def doit():
    paimon.speaking(input_1.get())


def fx_reader():
    x = XFServerAudio()
    x = x[-1]
    input_1.insert(0, x)
    paimon.speaking(x)
    del x


root = tk.Tk()
root.title("小派蒙学说话！")
root.geometry("400x600")
root["background"] = "#C9C9C9"
text = tk.Label(root, text="在下面输入你要让派蒙说的内容哦")
input_1 = tk.Entry(root)
button = tk.Button(root, text="点我我就说话了", command=doit)
button1 = tk.Button(root, text="开始录音", command=recording)
button2 = tk.Button(root, text="开始回答", command=fx_reader)
text.pack()
input_1.pack()
button.pack()
button1.pack()
button2.pack()
root.mainloop()
