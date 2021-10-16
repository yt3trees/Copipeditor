'''
メニュー生成モジュール
'''
import tkinter as tk
from tkinter import messagebox as mbox
import os
import webbrowser
import sys
from . import Global
from . import Shortcut
from logging import getLogger, StreamHandler, DEBUG, FileHandler
logger = getLogger(__name__)

class Menu:
    def create_menu(self, obj):
        # メニュー
        menubar = tk.Menu(obj)
        obj.master.config(menu=menubar)
        # ファイルタブ
        fileMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=fileMenu)
        fileMenu.add_command(label="保存", command = obj.save_item, accelerator="Ctrl+S")
        fileMenu.add_command(label="スタートメニューに追加", command = self.add_startmenu)
        fileMenu.add_separator()
        fileMenu.add_command(label="終了", command = lambda : obj.master.destroy(), accelerator="Alt+F4")
        # 編集タブ
        editMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="編集", menu=editMenu)
        editMenu.add_command(label="追加", command = lambda : obj.treeOpe.insert_tree(obj.tree), accelerator="Ctrl+N")
        editMenu.add_command(label="削除", command = lambda : obj.treeOpe.delete_item(obj.tree), accelerator="Delete")
        editMenu.add_command(label="全選択", command = lambda : obj.treeOpe.all_select_item(obj.tree), accelerator="Ctrl+A")
        editMenu.add_command(label="上と並び替え", command = lambda : obj.treeOpe.move_up_item(obj.tree,"up"), accelerator="K")
        editMenu.add_command(label="下と並び替え", command = lambda : obj.treeOpe.move_up_item(obj.tree,"down"), accelerator="J")
        editMenu.add_command(label="上に複製", command = lambda : obj.treeOpe.copy_item(obj.tree, "up"), accelerator="Shift+Alt+K")
        editMenu.add_command(label="下に複製", command = lambda : obj.treeOpe.copy_item(obj.tree, "down"), accelerator="Shift+Alt+J")
        # 実行タブ
        execMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="実行", menu=execMenu)
        execMenu.add_command(label="コピー処理実行", command = lambda : obj.copy_callback(), accelerator="F5")
        # ヘルプタブ
        helpMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=helpMenu)
        helpMenu.add_command(label="FAQ", command=self.open_faq)
        helpMenu.add_command(label="バージョン情報", command = lambda : self.open_version(obj))

    def open_faq(self):
        return

    def open_version(self, obj):
        obj.winv = tk.Toplevel()
        lw = 430
        lh = 150
        obj.winv.geometry(str(lw)+"x"+str(lh)+"+"+str(int(Global.ww/2-lw/2-10))+"+"+str(int(Global.wh/2-lh/2-15)))
        #obj.winv.geometry("400x150+975+575")
        obj.winv.title("バージョン情報")
        obj.winv.grab_set()
        obj.winv.attributes("-toolwindow", True)
        obj.winv.focus_set()

        # アイコン
        obj.img = tk.PhotoImage(data = Global.ICON)
        obj.img = obj.img.subsample(6, 6) # 縮小
        obj.canvas = tk.Canvas(obj.winv, width = 90, height = 90)
        obj.canvas.grid(row= 0 , column = 0, rowspan=10)
        obj.canvas.create_image(0 , 0, image = obj.img, anchor = tk.NW)

        # ツール情報
        title = 'Copipeditor ' + Global.VERSION
        versionInfo = 'Copyright © 2021 ytmori All rights reserved.'
        versionInfo2 = 'Source： ' + Global.SOURCE
        versionInfo3 = 'Python： v3.9.7'

        obj.label = tk.Label(obj.winv, font=("MSゴシック", "14"), text = title, justify='left')
        obj.label.grid(row= 0 , column = 1, sticky = "NW", pady=5)
        obj.label2 = tk.Label(obj.winv, font=("MSゴシック", "11"), text = versionInfo, justify='left')
        obj.label2.grid(row= 1 , column = 1, sticky = "NW")
        obj.labelSource2 = tk.Label(obj.winv, font=("MSゴシック", "11"), text = versionInfo2, justify='left')
        obj.labelSource2.bind("<Button-1>", lambda e: self.link_open())
        obj.labelSource2.grid(row= 2 , column = 1, sticky = "NW")
        obj.labelPython = tk.Label(obj.winv, font=("MSゴシック", "11"), text = versionInfo3, justify='left')
        obj.labelPython.grid(row= 3 , column = 1, sticky = "NW")
        obj.okButt = tk.Button(obj.winv, text = "OK", width=10)
        obj.okButt.bind("<Button-1>", lambda c: obj.winv.destroy())
        obj.okButt.place(x = 175, y = 120)

        # ショートカット
        shortcut = Shortcut.Shortcut()
        shortcut.define("menu", obj)

    def link_open(self):
        msbox = mbox.askokcancel("確認", "ブラウザでリンクを開きます。\r\n" + Global.SOURCE)
        if msbox == True:
            webbrowser.open(Global.SOURCE)

    def add_startmenu(obj):
        '''スタートメニューにアプリを追加'''
        try:
            cmdFile = os.path.dirname(sys.argv[0]) + "/script/run_スタートメニューに追加.bat"
            logger.info(cmdFile)
            os.system(cmdFile)
        except Exception as e:
            obj.error_message(e)