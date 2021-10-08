# tikinterライブラリの読み込み
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Checkbutton, messagebox as mbox
import os
import shutil
from distutils import dir_util
from tkinter import filedialog
import json
from typing import Text
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget
import sys
#from PIL import Image, ImageTk
import webbrowser
import glob
import datetime
from ttkwidgets import CheckboxTreeview

# グローバル変数
VERSION = "v0.5"
PARAM = os.path.dirname(sys.argv[0]) + "\param.json"
SOURCE = "https://github.com/"
btColorOk = "#83ccd2"
btColorDel = "#f6bfbc"
btColorCan = "#c0c6c9"

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack(expand=1, fill=tk.BOTH, anchor=tk.NW)
        self.master.title("コピーツール")

        self.ww = self.master.winfo_screenwidth()
        self.wh = self.master.winfo_screenheight()
        lw = 750 # self.master.winfo_width()
        lh = 314 # self.master.winfo_height()
        self.master.geometry(str(lw)+"x"+str(lh)+"+"+str(int(self.ww/2-lw/2-10))+"+"+str(int(self.wh/2-lh/2-15)) )
        #self.master.geometry("750x314+800+500")
        self.master.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(data=ICON))

        self.win = None # サブメニュー重複対策
        self.create_widgets()
        self.create_menu()

        # jsonファイル読み込み
        try:
            if os.path.exists(PARAM):
                jsonOpen = open(PARAM,"r")
                jsonLoad = json.load(jsonOpen)
                i = 0
                for j in jsonLoad.values():
                    if i == 0:
                        self.logFolder = jsonLoad.get('logFolder')
                        self.bkEnt.insert(tk.END, self.logFolder)
                    else:
                        self.tree.insert("", "end", iid=j['id'], text=j['id'], values=( j['from'], j['to']))
                    i = i + 1
        except Exception as e:
            e = "jsonファイルの読み込みに失敗しました。\n" + str(e)
            self.error_message(e)
            self.master.destroy()

# ---------------------------------------- メイン画面 From ---------------------------------------- #
    def create_widgets(self):
        # s = ttk.Style()
        # s.theme_use('winnative')
        # self.tree = ttk.Treeview(self)
        self.tree = CheckboxTreeview(self)
        self.tree["columns"] = (1,2)
        self.tree["show"] = "tree","headings"

        self.tree.heading("#0",text="ID",command = self.all_select_item)
        # self.tree.heading(1,text="ID")
        self.tree.heading(1,text="コピー元")
        self.tree.heading(2,text="コピー先")
        self.tree.column("#0",width=120)
        # self.tree.column(1,width=65)
        self.tree.column(1,width=290)
        self.tree.column(2,width=290)
        self.tree.bind('<Double-1>', lambda c: self.on_double_click()) # ダブルクリック
        self.tree.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=5)

        self.bkLbl = tk.Label(self, text = "バックアップフォルダ: ")
        self.bkLbl.grid(row = 1, column = 0)
        self.bkEnt = tk.Entry(self, width = 74)
        self.bkEnt.grid(row = 1, column = 1, sticky="W", pady=0, columnspan=3)
        self.bkFolderButt = tk.Button(self, text = "フォルダ", width = 10)
        self.bkFolderButt.bind("<Button-1>", lambda e: self.folder_dialog(self.bkEnt))
        self.bkFolderButt.grid(row = 1, column = 4, sticky = "W")

        self.addButt = tk.Button(self, text="追加", width=20)
        self.addButt.bind("<Button-1>", lambda c: self.insert_tree())
        self.addButt.grid(row=2, column=0, sticky="E", pady=5)

        self.delButt = tk.Button(self, text = "削除", width=20, bg = btColorDel)
        self.delButt.bind("<Button-1>", lambda c: self.delete_item())
        self.delButt.grid(row=2, column=1, sticky="E")

        self.allButt = tk.Button(self, text="全選択/全解除", width=20)
        self.allButt.bind("<Button-1>", lambda c: self.all_select_item())
        self.allButt.grid(row=2, column=2, sticky="E")

        self.button = tk.Button(self, text="実行", width=20, bg = btColorOk)
        self.button.bind("<Button-1>", lambda c: self.exec_copy())
        self.button.grid(row=2, column=3, sticky="E")

        self.saveButt = tk.Button(self, text = "保存", width=20)
        self.saveButt.bind("<Button-1>", lambda c: self.save_item())
        self.saveButt.grid(row=2, column=4, sticky="E")

        self.kakushiLbl = tk.Label(self.win, text = "( ^_^)b", font=("メイリオ", "25"))
        self.kakushiLbl.place(x=1000,y=500)

        # self.tree.bind("<<TreeviewSelect>>", lambda c: self.check_item())

        # ショートカット
        self.master.bind("<Return>", self.tree.bind('<Double-1>')) # Enterキー
        self.master.bind("<Control-n>", self.addButt.bind("<Button-1>")) # 追加
        self.master.bind("<Delete>",  self.delButt.bind("<Button-1>")) # 削除
        self.master.bind("<Control-a>", self.allButt.bind("<Button-1>")) # 全選択
        self.master.bind("<F5>", self.button.bind("<Button-1>")) # 実行
        self.master.bind("<Control-s>", self.saveButt.bind("<Button-1>")) # 保存
        self.master.bind("<k>", lambda c: self.move_up_item("up")) # 上に並び替え
        self.master.bind("<j>", lambda c: self.move_up_item("down")) # 下に並び替え
        self.master.bind("<Shift-Alt-K>", lambda c: self.copy_item("up")) # アイテムを複製
        self.master.bind("<Shift-Alt-J>", lambda c: self.copy_item("down")) # アイテムを複製
        self.master.bind("<Button-2>", lambda c: self.copy_item("down")) # アイテムを複製
        self.master.bind("<Escape>", lambda c: self.tree.selection_remove(self.tree.selection())) # 選択解除
        self.master.bind("<space>", lambda c: self.check_item()) # チェック
        self.master.bind("<Button-3>", lambda c: self.check_item()) # チェック

    def insert_tree(self):
        i = 0
        m = ""
        num = len(self.tree.get_children()) # 全アイテム数
        print("-----")
        while True: # breakするまで永遠ループ
            print(">>",m,"ループ処理開始",sep="")
            for item in self.tree.get_children():
                print('候補:',i,'重複チェック先:',self.tree.item(item)['text'])
                if i == self.tree.item(item)['text']: # IDが重複しているかチェック
                    print("iid一致データあり\n")
                    i = i + 1 # 重複した場合は
                    m = "再"
                    break
                m = ""
            if m == "":
                break
        print("ID:「", i, "」で作成しました。", sep="")
        self.tree.insert("", "end", iid=i, text=i, value=("","",""))
        return "break"

    def check_item(self):
        for item in self.tree.selection():
            if self.tree.tag_has('unchecked', item):
                self.tree.change_state(item, 'checked')
            else:
                self.tree.change_state(item, 'unchecked')

    def exec_copy(self):
        try:
            print (self.tree.get_checked())
            if self.tree.get_checked() == []:
                mbox.showwarning("アラート", "実行対象を選択してください。")
                return "break"

            td = str(datetime.date.today())
            today = td.replace("-", "") #yyymmdd
            t = str(datetime.datetime.now().time())[0:6]
            time = t.replace(":","")
            dateNow = today + time

            msbox = mbox.askokcancel("確認", "コピーを実行します。")
            if msbox == True: # OKボタン押下
                logFolderNow = self.bkEnt.get()+ "/" + dateNow
                if not os.path.exists(logFolderNow):
                    os.mkdir(logFolderNow)

                selected_items = self.tree.get_checked() # 行データの取得
                print (selected_items)
                for item in selected_items:
                    row_data = self.tree.item(item)

                    # 列データの取得
                    row_value = row_data['values']
                    id = row_data['text']
                    fromPath = row_value[0]
                    toPath = row_value[1]
                    if not os.path.exists(toPath):
                        message = "パス'" + toPath + "'は存在しません。"
                        mbox.showerror("エラー", message)
                        return "break"

                    logFolderNowID = logFolderNow + "/" + id
                    logFolderNowFrom = logFolderNowID + "/" + "After"
                    logFolderNowTo = logFolderNowID + "/" + "Before"
                    if not os.path.exists(logFolderNowFrom):
                        os.makedirs(logFolderNowFrom)
                    if not os.path.exists(logFolderNowTo):
                        os.makedirs(logFolderNowTo)

                    os.chdir(toPath) # toフォルダに移動
                    print("カレントディレクトリ:",os.getcwd())
                    if os.path.exists(fromPath):
                        searchPath = fromPath + "/**/*"
                        i = []
                        files = ([p for p in glob.glob(searchPath, recursive=True)
                            if os.path.isfile(p)]) # コピー元ファイル一覧取得
                        print (files)

                        # コピー先重複ファイルバックアップ処理
                        for file in files:
                            print("From:",file) # コピー元ファイル名
                            fileAfter = file.replace(fromPath, toPath) # コピー先ファイル存在確認用文字列生成
                            print("To:",fileAfter) # コピー先ファイル名
                            print("比較:", os.path.exists(fileAfter),"\r\n----------")
                            if os.path.exists(fileAfter):
                                toFile = fileAfter.replace(toPath, "")
                                logFolderNowToFile = logFolderNowTo + "/" + toFile[1:]
                                print (">>",toFile[1:],"から",logFolderNowToFile,"にコピーします。")
                                toFile = "./" + toFile
                                if not os.path.exists(os.path.dirname(logFolderNowToFile)):
                                    os.makedirs(os.path.dirname(logFolderNowToFile))
                                shutil.copy2(toFile, logFolderNowToFile)
                                print (">>",toFile[1:],"から",logFolderNowToFile,"にコピーしました。")

                        dir_util.copy_tree(fromPath, logFolderNowFrom) # コピー元ファイルをバックアップフォルダにコピー
                        dir_util.copy_tree(fromPath, toPath)
                        print ('実行：',fromPath,toPath)
                        dir_util._path_created = {} # キャッシュをクリア
                    else:
                        message = "パス'" + fromPath + "'は存在しません。"
                        mbox.showerror("エラー", message)
                        return "break"
            return "break"
        except Exception as e:
            self.error_message(e)

    def delete_item(self):
        selected_items = self.tree.get_checked() # 行データの取得
        for item in selected_items:
            self.tree.delete(item)

    def all_select_item(self):
        allItem = self.tree.get_children()
        checkedItem = self.tree.get_checked()
        if len(allItem) != len(checkedItem): # 選択されていないアイテムが1つでもあれば全選択
            for i in allItem:
                self.tree.change_state(i, 'checked')
        else:
            for i in allItem:
                self.tree.change_state(i, 'unchecked')

    def save_item(self):
        msbox = mbox.askokcancel("確認", "設定を保存します。")
        try:
            if msbox == True:
                self.tree.selection_set(self.tree.get_children())
                selected_items = self.tree.selection() # 行データの取得

                i = 0
                a = {'logFolder':self.bkEnt.get()}
                for item in selected_items:
                    row_data = self.tree.item(item)
                    row_value = row_data['values']

                    if row_data['text'] == '':
                        raise ValueError("IDが入力されていないデータが存在します。")

                    a[i] = {'id':row_data['text'],'from':row_value[0],'to':row_value[1]}
                    i += 1

                with open(PARAM, 'w') as f:
                    json.dump(a, f, indent=4, ensure_ascii=False)

                self.tree.selection_remove(self.tree.selection())
                mbox.showinfo('確認', '保存しました。')
            return "break"
        except Exception as e:
            self.error_message(e)

    def move_up_item(self, m):
        if m == "up":
            cal = 1
        elif m == "down":
            i = len(self.tree.get_checked()) # 選択アイテム数
            cal = -i # 複数選択の場合、複数選択分まとめて移動
        for selected_item in self.tree.get_checked():
            self.tree.move(selected_item, self.tree.parent(selected_item), self.tree.index(selected_item) - cal)

    def copy_item(self, m):
        if m == "up":
            cal = 0
        elif m == "down":
            cal = len(self.tree.get_checked())
        a = 0
        for item in self.tree.get_checked() :
            idx = self.tree.index(item)
            if m == "up" and a > 0:
                idx = idx -a
            itemValue = self.tree.item(item)['values']
            self.tree.insert('', idx+cal, values = (itemValue))
            a += 1
        return True

    def error_message(self, message):
        msg = "エラーが発生しました。\n" + str(message)
        mbox.showerror("Error!", msg)

# ---------------------------------------- メイン画面 To ---------------------------------------- #
# ---------------------------------------- サブ画面 From ---------------------------------------- #
    def on_double_click(self): # https://try2explore.com/questions/jp/12101569
        # ダブルクリック時チェックボックスの状態を反転
        # if self.tree.tag_has('unchecked', self.tree.selection()):
        #     self.tree.change_state(self.tree.selection(), 'checked')
        # else:
        #     self.tree.change_state(self.tree.selection(), 'unchecked')

        #a = self.tree.selection()
        if () == self.tree.selection(): return
        if self.win == None: # 重複して開かない
            self.win = tk.Toplevel()
            lw = 400
            lh = 100
            self.win.geometry(str(lw)+"x"+str(lh)+"+"+str(int(self.ww/2-lw/2-10))+"+"+str(int(self.wh/2-lh/2-15)))
            # self.win.geometry("400x100+975+600")
            self.win.title("Edit Entry")
            # self.win.attributes("-topmost", True)
            # self.win.attributes("-toolwindow", True)
            self.win.grab_set()
            self.win.focus_set()

        # 行データの取得
        selected_items = self.tree.selection()
        row_data = self.tree.item(selected_items[0])

        # 列データの取得
        row_value = row_data['values']
        # title = row_value[0]
        title = row_data['text'] # id
        fromPath = row_value[0] # from
        toPath = row_value[1] # to

        self.col1Lbl = tk.Label(self.win, text = "ID: ")# 一意になるように制限
        self.col1Ent = tk.Entry(self.win, width = 20)
        self.col1Ent.insert(0, title)
        self.col1Lbl.grid(row = 0, column = 0)
        self.col1Ent.grid(row = 0, column = 1, sticky="W")

        self.col2Lbl = tk.Label(self.win, text = "コピー元: ")
        self.col2Ent = tk.Entry(self.win, width = 50)
        self.col2Ent.insert(0, fromPath)
        self.col2Lbl.grid(row = 1, column = 0)
        self.col2Ent.grid(row = 1, column = 1, columnspan = 2)

        self.folderButt = tk.Button(self.win, text = "フォルダ", width = 5)
        self.folderButt.bind("<Button-1>", lambda e: self.folder_dialog(self.col2Ent))
        self.folderButt.grid(row = 1, column = 3, sticky = "W")

        self.col3Lbl = tk.Label(self.win, text = "コピー先: ")
        self.col3Ent = tk.Entry(self.win, width = 50)
        self.col3Ent.insert(0, toPath)
        self.col3Lbl.grid(row = 2, column = 0)
        self.col3Ent.grid(row = 2, column = 1, columnspan = 2)

        self.folder2Butt = tk.Button(self.win, text = "フォルダ", width = 5)
        self.folder2Butt.bind("<Button-1>", lambda e: self.folder_dialog(self.col3Ent))
        self.folder2Butt.grid(row = 2, column = 3, sticky = "W")

        def update_then_destroy():
            if self.confirm_entry(self, self.col1Ent.get(), self.col2Ent.get(), self.col3Ent.get()):
                self.win.destroy()
                self.win = None

        # OKボタン
        self.okButt = tk.Button(self.win, text = "OK", bg = btColorOk, width = 5)
        self.okButt.bind("<Button-1>", lambda e: update_then_destroy())
        self.okButt.place(x = 263, y = 73)
        # Cancelボタン
        self.canButt = tk.Button(self.win, text = "Cancel", bg = btColorCan, width = 5)
        self.canButt.bind("<Button-1>", lambda c: self.close_window())
        self.canButt.place(x = 308, y = 73)
        # Deleteボタン
        self.delButt = tk.Button(self.win, text = "Delete", bg = btColorDel, width = 5)
        self.delButt.bind("<Button-1>", lambda c: self.tree.delete(self.tree.focus()) & self.close_window)
        self.delButt.place(x = 353, y = 73)

        # xボタン押下時の制御変更
        self.win.protocol('WM_DELETE_WINDOW', self.close_window)

        # ショートカット
        self.win.bind("<Escape>", lambda c: self.close_window()) # サブメニューを閉じる
        self.win.bind("<Return>", lambda e: update_then_destroy()) # 入力内容確定

    def close_window(self): # サブメニュー重複対策
        self.win.destroy()
        self.win = None
        return "break"

    def folder_dialog(self,obj):
        try:
            dir = obj.get()
            print(dir)
            fld = filedialog.askdirectory(initialdir = dir)
            if fld != "":
                obj.delete(0,tk.END)
                obj.insert(tk.END,fld)
            return "break"
        except Exception as e:
            self.error_message(e)

    def confirm_entry(self, tree, entry1, entry2, entry3):
        currInd = self.tree.index(self.tree.focus())
        self.delete_current_entry(self)
        self.tree.insert('', currInd, iid = entry1, text = entry1, values = (entry2, entry3))
        return True

    def delete_current_entry(self, treeView):
        curr = self.tree.focus()
        if '' == curr: return
        self.tree.delete(curr)
# ---------------------------------------- サブ画面 To ---------------------------------------- #
# ---------------------------------------- メニュー画面 From ---------------------------------------- #
    def create_menu(self):
        # メニュー
        menubar = tk.Menu(self)
        self.master.config(menu=menubar)
        # ファイルタブ
        fileMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=fileMenu)
        fileMenu.add_command(label="保存", command = self.save_item, accelerator="Ctrl+S")
        fileMenu.add_command(label="スタートメニューに追加", command = self.add_startmenu)
        fileMenu.add_separator()
        fileMenu.add_command(label="終了", command = lambda : self.master.destroy(), accelerator="Alt+F4")
        # 編集タブ
        editMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="編集", menu=editMenu)
        editMenu.add_command(label="追加", command = self.insert_tree, accelerator="Ctrl+N")
        editMenu.add_command(label="削除", command = self.delete_item, accelerator="Delete")
        editMenu.add_command(label="全選択", command = self.all_select_item, accelerator="Ctrl+A")
        editMenu.add_command(label="上と並び替え", command = lambda : self.move_up_item("up"), accelerator="K")
        editMenu.add_command(label="下と並び替え", command = lambda : self.move_up_item("down"), accelerator="J")
        editMenu.add_command(label="上に複製", command = lambda : self.copy_item("up"), accelerator="Shift+Alt+K")
        editMenu.add_command(label="下に複製", command = lambda : self.copy_item("down"), accelerator="Shift+Alt+J")
        # 実行タブ
        execMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="実行", menu=execMenu)
        execMenu.add_command(label="コピー処理実行", command = lambda : self.exec_copy(), accelerator="F5")
        # ヘルプタブ
        helpMenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=helpMenu)
        helpMenu.add_command(label="FAQ", command=self.open_faq)
        helpMenu.add_command(label="バージョン情報", command=self.open_version)

    def open_faq(self):
        return

    def open_version(self):
        self.winv = tk.Toplevel()
        lw = 400
        lh = 150
        self.winv.geometry(str(lw)+"x"+str(lh)+"+"+str(int(self.ww/2-lw/2-10))+"+"+str(int(self.wh/2-lh/2-15)))
        #self.winv.geometry("400x150+975+575")
        self.winv.title("バージョン情報")
        self.winv.grab_set()
        self.winv.attributes("-toolwindow", True)
        self.winv.focus_set()

        # アイコン
        self.img = tk.PhotoImage(data = ICON)
        self.img = self.img.subsample(6, 6) # 縮小
        self.canvas = tk.Canvas(self.winv, width = 90, height = 90)
        self.canvas.grid(row= 0 , column = 0, rowspan=10)
        self.canvas.create_image(0 , 0, image = self.img, anchor = tk.NW)

        # ツール情報
        title = 'コピーツール ' + VERSION
        versionInfo = 'Copyright © 2021 ytmori All rights reserved.'
        versionInfo2 = 'Source： ' + SOURCE
        versionInfo3 = 'Python： v3.9.7'

        self.label = tk.Label(self.winv, font=("MSゴシック", "14"), text = title, justify='left')
        self.label.grid(row= 0 , column = 1, sticky = "NW", pady=5)
        self.label2 = tk.Label(self.winv, font=("MSゴシック", "11"), text = versionInfo, justify='left')
        self.label2.grid(row= 1 , column = 1, sticky = "NW")
        self.labelSource2 = tk.Label(self.winv, font=("MSゴシック", "11"), text = versionInfo2, justify='left')
        self.labelSource2.bind("<Button-1>", lambda e: self.link_open(SOURCE))
        self.labelSource2.grid(row= 2 , column = 1, sticky = "NW")
        self.labelPython = tk.Label(self.winv, font=("MSゴシック", "11"), text = versionInfo3, justify='left')
        self.labelPython.grid(row= 3 , column = 1, sticky = "NW")
        self.okButt = tk.Button(self.winv, text = "OK", width=10)
        self.okButt.bind("<Button-1>", lambda c: self.winv.destroy())
        self.okButt.place(x = 160, y = 120)

        # ショートカット
        self.winv.bind("<Escape>", lambda c: self.winv.destroy()) # サブメニューを閉じる
        self.winv.bind("<Return>", lambda e: self.winv.destroy()) # サブメニューを閉じる

    def link_open(self,link):
        msbox = mbox.askokcancel("確認", "ブラウザでリンクを開きます。\r\n" + link)
        if msbox == True:
            webbrowser.open(link)

    def add_startmenu(self):
        try:
            cmdFile = os.path.dirname(sys.argv[0]) + "/script/run_スタートメニューに追加.bat"
            print (cmdFile)
            os.system(cmdFile)
        except Exception as e:
            self.error_message(e)

# ---------------------------------------- メニュー画面 To ---------------------------------------- #

# icon\copytool.gif
ICON = '''
        R0lGODlhAAIAAqIAAAAAAC6A/jSZ/00zTf97Uf+RWv///wAAACH5BAUKAAAALAAA
        AAAAAgACAAP/CLrc/jDKSau9OOvNu/9gKI5kaZ5oqq5s675wLM90bd94ru987//A
        oHBILBqPyKRyyWw6n9CodEqtWq/YrHbL7Xq/4LB4TC6bz+i0es1uu9/wuHxOr9vv
        +Lx+z+/7/4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6Slpqeo
        qaqrrK2ur7CxsrO0tba3uLm6u7y9UQbAwcLDxMXGx8jJysvMzc7P0NHS09TBvlLV
        2drb3N3e3+DL17/h5ebn6OnqyONQ6+/w8fLzxe1P9Pj5+vvT9k78AAMK5OevycCD
        CBOaK8hEocOHEKExXBKxosWLwCYqwcix/+NBjUk8ihyJDyQSkihTpjN5RKXLl91Y
        GoFJs2Y0mUVs6tzJDucQnkCDGvA5IpyAo0iTKl3KtKnTp1CjHnVWoKrVq1izat3K
        tavXr2DDih1LVms4kEalql3Ltm1SqmXjyp1Lt67dr2c1pnXLt69fuHcDCx5MuG7e
        iXv9Kl4MFXDhx5AjPz7MMDHjy5gFOJbMubPnsJQLWs5Muu/mz6hTfw7tb3Tp12tP
        q55NezBre65h634qu7bv32Vvt8u9u7jS3sCTK98qfBxx49CRL5++vPm159CLS6fO
        3bd1X9iz697evXzq773Ci39N3rx7zuh5qV9Puv37+4Xj75pPH7N9/P8A3qWfLvz1
        x9h/ASYo14CZFGjgg401o+CECTqDiYMQZrgUghR2SJuFl2Co4YiaSejhid2BaImI
        JGbIIYowSqZiJSy2+OCLMeZI2IyU1GhjfzjqKKRdPE7i44/rBTnkknEVKcmRSGan
        JJNUgtbMheBEqeVxJlbp5Y5XhpjllmRO+eWZWDkZCZRkjtclmnAuGOaKY7YZpZlx
        nqkmJGzaWRqeeXq55yN9+pkZoIFSOagjhRp6GaKJLrloI406uhikkQo5KR/OWOop
        X5hmmuima3T66alqhSpqnqSqYSqqsDql6qpwtprGq7Hm+tabtPYqlq1o4KqrrrP6
        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
        Ndc7qtU+r6nb1e0mr2nc3w4ZurdY2oRfl+ErLvfflD3ZZz865Fe+dqPXHfF//7Dg
        iV15sDje2HZvLt69y3U0Jj7Srcde6b9y+ounnrurb2/sfzJ7wu1egL3vSu1J7ve7
        dz7vmqcC38O++ZkD3umjB7dbtzX5qr++04u/PmqGH/Os83lbNj0l5RlP3d/zlPyF
        4b7SvT99tYV/k+PXPq7NX8Pgc0X9fS+B/9eN835Nxj/0xZV9AHhymfd5+vd909J/
        jvR/zid6yZdw8ucZ+Md8std+YKOAjcSATAc8AtiAmLdx0cdaFlg1GMhIGohb1BOC
        rGZ/WzGBbXeAI6g0JQhIJ4hdKfiAgzeABVaAj1eBkec3M/hHNXheN2iAaaeDquGC
        hweDP0g3QehHQ2hfRdiDEIiEqaGEUIeAy/KEfRSFIzaFqFd8G2h2IIiD59eE7rdI
        qOSFMAaGtieGKPh82EZ/vqaFw8KFfMSGwVBYt2eDcmhudKhtdkgsaih+1meFqqaC
        1saCWoGF7IeGF1iI8HeIHihfilhvjJgVjth1g5greLhHenhnbkh8zf83hh8YeGZY
        fzH4M5+oR6FYaKPYfXDoh2SIikaIP8xwNQtDUkdYiYoXiOSWiVhhYJvIhMqgiwPD
        i1Xoi7B3idIkjFdBjDwYhsaYDMi4L8qYg8yIfcCIbtBoFdJYhrcIfLnYNLv4cEsX
        hw44jmeIiJ8RjrZIheS4DNc4L9lIeugXYUqmdfC4XPvYDPW4LvcofREIb/+Yj4PR
        j3PojD1Wjkxzjt2INgh5H4/Dj/1YkQBpjsmIjn1IhBwYkQP3jVWhkIDIkEvmkEID
        kSb5inzIiRMZGCQZcCAJcRn5kBs5k+1TkAt3kDopGTEZdCupZSgZNCqZioYjkpGB
        kS/ZZD8JajP/6QwBOS4DuW9LiWVPiZRN6ZRB2WZDeTNFyY58g5SQoZQ9GRlZuVk8
        eYwaiY0cOYseuY7y2I7buH1nqVpX2ZU285VxGZZVWR5k6Y4SWJf+eJf0uJb22Jal
        qI4BSJiAqVWCeWBbuWd4WTN6SY0BI5aTAUfu8ZiQaZSFVJMpeZORqXyYmR+aaR6c
        +ZfWaJgCiZi9aIqWOA8KkpppuZo2yZY4CUJlSVtaBCC0yZi2GZq4OZp7V5pg0pv4
        8ZvEKWqgSZSi6ZldsHzmMJuPqZrIEJXg55rLCJu/SA/UKZjWeQzYmYDaqY3c2Yyy
        mSDKCZ2g1Jxe+ZxgeZR9eWbeqZ7VWZvX/8maUlme+Lib5VefAbKe8fmZk7kylfmG
        +WKctnGa5SGgeymChXmbh5mbXeSf44Wc9+GglomLESqcE7qc5DCfdcag3aGhCOqD
        aimhrUmhrteYO4mh72GipIiiwemcw8meWyCd5fCddRmexjCeW8ifBOmiVwegvnmf
        wJmfKrqfLEoEFwU1SkhLWVigKnOgM5owCpo8czeNtDaJLtmhNvqhOKoFT1o0UbqG
        j5iiHrqiIBoyIqqldCmOcWaIX6qmYcqmY5oFZaozZ0qn1aika8qkbRozbwqngSmn
        jealfyqe+pmdTcp7hWqoesWl0KaoNAqodyqoecqSkmqfiNql/pemNf/6njc6oNGZ
        pZ16f5TKbpbKoXZKqmJqqlywpy7Tp606j6+al/D5oLiDqqnaiKt6cLcql5gKq3gq
        qznqq786jMFKUWhap6Oqq6XKq6caqctKGLYaqtBarNIaq9Q6q8p6rSPZrCD1rIv6
        o41Kno8qBLTqMdm6gKLKrZS5qxsaMeEqru+agfHKqNHDLUJKlRYqrlyGpINKoGDK
        O/66rkHQrpkio7KYmOjar54ylStorQKrquDZgfLqOQlbsMwTsBcrFw67fm5JDNzT
        sZtKiecZso8xsvn3mvwKPSiLrGR6r4PjshS4nTFrPDP7rclqsSzLrBmrsLrmnrLT
        s/WKNEAbtOD/SLApu607i7AT+68VC7JMu6VD67HtSaWKg7QniqVLe7U4+4IwG7Ey
        O7VE+wMMGylju4RlWwwni7ZaK5FWe7Wm57Q0O3RGizpee6X2GrZM27bpaLY8K7dP
        +3I2mzeC25Emuz19+7CXCbhBu7glOwxxSy5Uu4iSy7KUC7Fw67iGm7ecCqec2bZS
        yriWC7qYm7Y+sLZJWLpZS2V++raNK7GrO7dys7mJAruxO2azq7OEK7W3e7ikqbuB
        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
        tNqLs968RwOG4mgM5ommA8C27gvH8kzX9o3H6n6SfhgICofEovGITCqXTKLnCY1K
        p9Sq1fH78Xi5rvcLDotZ213W10yr1+y2+w2Py+f0uv19JpVV477//7WXkjdyZ3iI
        mKi4yNjoGEAoIogCWGl5STZpEgn06PkJGio6+skJommCqboKhjpgakAqO0tbazsK
        68q6y0vjCnsbLDxMXIyUi9qrvAzwa2oMHS09zYisyYzN6sxJ3e39Da5kPZldfrkd
        Ga6+zm48Lmge/4dO2G5/jw/6viffL0afJ5/AgQTp7CvjL6EXgGcKOv98CDHJwS0K
        K95gmCWixo0OJ3KxCFIGxh8cS5ps53FHyJUvRqI5CTPmtJR8WNp0SUKmzp3CaKaw
        eRMVMJ5Ei4rySQmoUhs4YRUyCrUk0hNLq84T6pRb1K0Rp6ayCjZM06wguJrtaEpX
        2LVdxpI9C1eg1xVs6zLFSjZg3L0o0yazC1gk3rwZ+RoONzew4paDCb88DJla4sWU
        3WaNjFnaZMqKLTvNDLrYZs6APQ8NjdrWaNJ1TT9LDXvWatZrXWuNjTvUbNpgbafL
        DdzTbt5VfdcLjrya32vE2RrXmzz6oeHNgT5vKD27HerVF7u6Xlh7XO7dy7f43tjx
        U/FwyZsvj17/k/rw7M26f189/qT5JOufvY8fcfoJwt9j/m0FYIC0DbhHgTkdyFWC
        CpLGYBkOrgchVBJOWFmFPFwoQoYILkcOhwF6+CGIZYmoIYnwmIgfimaoGAuLRm0I
        Y2kyDkKjjTe6yE+O5u3Io4o+FoWjkM4R2UOPR/KUpJJhMdmkkU/uFKWUVlG5iZNX
        ypSllktx+YqXX8IUppgckkljm26+CSd0uACJkJp2AsJmnHruySd/stFJ0Z2CjpFn
        n4Yeimh/pKQ5qJ2FJgpppHv+yYlajV6aw6OSbsrphZRGYimmovrCZaemnqrep4SE
        OmqrjFGJaqyy3jZnpX+5iut5pc7Ka68h/8rCaK5r7uprsbKqmgerwo6qqbHObors
        Gcoui2mzz16LaLRZTEtto9ZiC+6kwAL6UbfMEhtuuuIuSq5K5p4Lq7ryxqmtFre+
        e+m38+7r57i2ModvvujyS3C/7P5bYsAKZ0pmww4/jOJpdwS7cMUuQIxxxhpb+Joh
        FFts8cYij4yxxNu1WxPIKv9Dcssu72hyHR+vHPDLNt8cX8wGofwTzT63hXPQQm+h
        8xwz/9zt0EovXSatJyP8ItJSz8B01TgXLcfRU+dqddcuYx2H1lu76nXZIoMNh9hj
        w2t22w6jjQfPSa29ttt2Nwy3G2rTLfDdfsPc8cRyU8X32H8fHnHgT/+Dem/hSCMO
        +YB5t7G343dGjvl3k7NRueWev7s5JIN/9XnppnsReuenr15x6qPTxXrssrPgOtRB
        zo776bUzDnDuvlu++6qN/0782MEnO3zxyv98vLTJLw89yM1v+3z01gc8vb29X889
        9oqL83r34nvvNPi21zl++stm7wO36r/fKPt6VA9//WrKP4L79u+vJP6S0M+/AHKo
        TfoToAEFRUAAHnCBWkrg9hgIwfvRqIARrOCEHJgwC2owRxiM2gY/eMEJKhCEJGRN
        B29XwhRW54ToU6ELacPCQL1whpyJYbloiEPA2NBdOewhW3aYMh8KsSpA7NkQjwiU
        Is4NiUwEiRJdCdfEKCqETFKs4pS4ZMUsjgmLWuziSqjoxTBWBIxiLKM8yGjGNGID
        jWpsIy/Y6MY4YgKOcqzjVahkxzxWgo567CPQ8OjHQAaCi4Is5EUIachECgaQimzk
        q5gUvQQAADs=
        '''

root = tk.Tk()
app = Application(master=root)
app.mainloop()