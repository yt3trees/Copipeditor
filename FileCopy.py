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
        style = ttk.Style()
        style.theme_use("xpnative")

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
        self.pb = ttk.Progressbar(root, mode="indeterminate") # プログレスバー(非確定的モード)
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
                        self.progress_bar("start") # プログレスバー表示
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
                        self.progress_bar("stop") # プログレスバー終了
                        mbox.showinfo("アラート", "完了しました。")
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

    def progress_bar(self,param):
        if param == "start":
            self.winbar = tk.Toplevel()
            lw = 200
            lh = 45
            self.winbar.geometry(str(lw)+"x"+str(lh)+"+"+str(int(self.ww/2-lw/2-10))+"+"+str(int(self.wh/2-lh/2-15)))
            self.winbar.title("コピー中")
            self.winbar.grab_set()
            self.winbar.focus_set()
            self.winbar.Lbl = tk.Label(self.winbar, text = "コピー中...")
            self.winbar.Lbl.pack()
            self.winbar.pb = ttk.Progressbar(self.winbar, mode="indeterminate",length="180") #非確定的モード
            self.winbar.pb.start()
            self.winbar.pb.pack()
        elif param == "stop":
            self.winbar.destroy()
        return self.winbar.pb

# ---------------------------------------- メイン画面 To ---------------------------------------- #
# ---------------------------------------- サブ画面 From ---------------------------------------- #
    def on_double_click(self): # https://try2explore.com/questions/jp/12101569
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
        self.delButt.bind("<Button-1>", lambda c: self.tree.delete(self.tree.focus()) & self.close_window())
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
        R0lGODlhAAIAAvIAAAAAAP97Uf+RWi6A/jSZ/wAAAAAAAAAAACH5BAEAAAAAIf8L
        SW1hZ2VNYWdpY2sNZ2FtbWE9MC40NTQ1NQAh/wtYTVAgRGF0YVhNUDw/eHBhY2tl
        dCBiZWdpbj0n77u/JyBpZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4
        OnhtcG1ldGEgeG1sbnM6eD0nYWRvYmU6bnM6bWV0YS8nIHg6eG1wdGs9J0ltYWdl
        OjpFeGlmVG9vbCAxMi4xNic+CjxyZGY6UkRGIHhtbG5zOnJkZj0naHR0cDovL3d3
        dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyc+CgogPHJkZjpEZXNj
        cmlwdGlvbiByZGY6YWJvdXQ9JycKICB4bWxuczp0aWZmPSdodHRwOi8vbnMuYWRv
        YmUuY29tL3RpZmYvMS4wLyc+CiAgPHRpZmY6T3JpZW50YXRpb24+MTwvdGlmZjpP
        cmllbnRhdGlvbj4KIDwvcmRmOkRlc2NyaXB0aW9uPgo8L3JkZjpSREY+CjwveDp4
        bXBtZXRhPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAK
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        IAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg
        ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSd3
        Jz8+Af/+/fz7+vn49/b19PPy8fDv7u3s6+rp6Ofm5eTj4uHg397d3Nva2djX1tXU
        09LR0M/OzczLysnIx8bFxMPCwcC/vr28u7q5uLe2tbSzsrGwr66trKuqqainpqWk
        o6KhoJ+enZybmpmYl5aVlJOSkZCPjo2Mi4qJiIeGhYSDgoGAf359fHt6eXh3dnV0
        c3JxcG9ubWxramloZ2ZlZGNiYWBfXl1cW1pZWFdWVVRTUlFQT05NTEtKSUhHRkVE
        Q0JBQD8+PTw7Ojk4NzY1NDMyMTAvLi0sKyopKCcmJSQjIiEgHx4dHBsaGRgXFhUU
        ExIREA8ODQwLCgkIBwYFBAMCAQAALAAAAAAAAgACAAP+CLrc/jDKSau9OOvNu/9g
        KI5kaZ5oqq5s675wLM90bd94ru987//AoHBILBqPyKRyyWw6n9CodEqtWq/YrHbL
        7Xq/4LB4TC6bz+i0es1uu9/wuHxOr9vv+Lx+z+/7/4CBgoOEhYaHiImKi4yNjo+Q
        kZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/A
        wcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5dUE6Onq6+zt7u/w
        8fLoGAL29/j5+vv8/f7/AAMKHEiw4D5zKuYpXMiw4bp6BiNKnEixokWACFM43Mj+
        sSO9CxdDihxJ8mJGFB5TqowHsaTLlzBfnjyxsqbNjxZi6tzJ0+BMEzeDpmzZs6hR
        oz9LCF26kejRp1BLJiXBtOpCp1GzapU4dYTVryxBbh1LdmBXEWDTtsNatq1bAWdD
        qJ2bju3bu1rjgqBL1y7ev0f1fuA71y/gwzsFeyCs1jDixy4Vd2Cc1jHkyyElc6AM
        1jLmzxMzch7d0TPo02ORkV7d0DTq11BVs54tzzXs2z1l0969Vizu31t18x6OswLw
        41mFE+dtG7lzk8eWL2/+vDrX6NKHU7fO3Sz27Lu3dx/vTzn41eLJq89n/vzo9Ovj
        t3dPGX589fPpE7Z/f3z+fv19+dbfgBh9ByBn/BFY3X8HViagghCyd0qDFIaVU4QY
        XmdJhRz2dmGGIHq3YYckFkdBiCgGhEmJJSaYIn6XsEiiiy/6F6OMHNJYI3cr4lih
        jjsueKOPDQIZpHM9EnmgkUcel6SS+jHZ5G9PQumelFPeVqWV4GGZ5Wtbcimdl1+e
        FqaYxJFZ5mdnosncg2tG2KabtKkZJ2SI0MnYAHz26eefgAbqp513IpannnwJquii
        fxJaKGCHIjoXo5Qq6uijeEUqaVqVdtoonJjep+mmX3lq6gCXhurWqKRWdaqnqapa
        FqutLvVqp7HKmtohtYJ1a6W56poXr71a9SulwQr+GxWtxdp0LKPJKvsUs82u9Oyi
        0UqLFLHVCnWtpaBqK6Qh3dr6baDZissTteV2dC664aqLHLvtbvQuoOnKGxO99TZ0
        76cf6jtuHf3G8+/B8AaM5A0golEwPAhH3Ge+kTGcocMPuyOxxBRLZTGGGGfMzsYR
        d0wSDg2fIXI7JCNs8kgoX6zyyuu0fPDLIsUM8sw0p2Pzvzhn9rGcPPdMwM/3Bg2d
        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
        /3Tqv6P7Qzv/5Ud/4Hcn/gdv8heA+zeAcVKA4HYG+pcm/FcjDIhuDoiAEKiAazKB
        AFeBqCd9o6crGohwHHgwlEdu8hKCPoYGD6gdEfgiKNhiKmiBLIiBZfKCJBaDHZh9
        NPglNrhhOEiCold56tKDEvaDkxeEJjiERAhgRngvJchu+rKETHgHK/gmS4UZKCCF
        dccIVRged8BqJqCFYAcJXVgnX4iFJyCGZycJZTgbeACGJaCGTDcJbcgab4iGYSiH
        U0eHMmiFgXUZWaiHhVUJdYgeZwiIaSiISMaHOfh9f4gniaiID8eGfeiFV4iIeSiJ
        MceIQLj+fI/4GIGoiXTGiUfoiWmFiXEoiqNIiY3YfpcIiZmoipcWCYVIGneIiiQg
        i8lFiJVohq8IipGoi5hQi+9xiLCYiroIa6zYiR54iseYi8mojLTYi25ojMBoAQyB
        DcSIINZoKBeQjdewjfXRjYeBAeBoDeLIGLf4jBNwjtWQjvtBjpDyjVcRjtRoh/L4
        F+ZYj+h4j4b4i96Ijfz4jv5oi/mYKfSoENpYkMUIkOWYkPOwkK0ogJ8YkBXgjtQA
        j3yxjtd4kQOZkQzJjQ45jwKpkPY4kQlYkQ9ZkhF5ksyogypJkh5pkv2IkhcYk/oI
        kbXhkqXYjBuFi+34kdOwOHzyhGH+EI3SCAFMgQxEOQBGCQZIuY9CwZRE+ZRfEJU6
        aRNUuThW6QVYyZI3sZWD05Vd8JUzGRRiqTdkyQVmSQFLeQxNuZZb0JZBOZVwWZVI
        KAZ0KQFvaQxxmZdHGY1SiZZ3yZWACZWCmZU1kZZyI5dasJcR0JfF8JemOAaQqZRL
        wZhq45hZcJkPIJnEQJk+qZeJCZZaWZhjeZhXWZpnGZaoqZaq6ZWs6ZaZyZONOW6S
        8I+TiZe7Rgm6GZq8uW2+aZB+GZxWN5wNuZuG2ZuT8JvDIJrH2ZzEqZypyZy5OZ3A
        uZzCKZ3JmZ3VuZ3X2Z3PaZzTVgnOKQzQWZ7IKZLUCZvWGQn+5xkM6fl05omd46md
        0Rme7Omd7gme8Gmf6Eme9Lme41icTWmTgZOgpXELBxqSCvqgHlILDYqgEFqhO2kL
        E/qSFrqhNCmhGeqEHBqiHUoLHwqiInqi74ALJfouKNqiEUqiK/otLjqjdcGgMXot
        NEqjKnqjz5KjM7qjPPorPuqiQBqkrzKkLVqkRgp3SEozSrqkTtekEPqkUKpsUsqh
        VFql6nalWPqaWmqiXNovWfqlOBqmBTOmZHosZnqmNpqmYLqm3YKmbnqkcNoucjqn
        TFqnXHKneBqleopdbdqnPfqnvQWjgjqohGpeGHqoiJqoqhWojEqnjvqoixqptzKp
        owX+qZaadpi6p5q6qVXXqXrCp6D6J6IKqJVaqn56qgvnC6r6qrAaqxCUqrJaq7a6
        qaR6q7q6qzyaq7z6q8DalL4arMRarEgzrMaarMrqPrS6rM76rPUzC9A6rdSaNJ9a
        rdiarQPUrNrard46Mdf6reJarcg6rub6q+V6rupqq+m6ru76qu36rvJqqfE6r/ba
        pxJ5r/p6rAixr/76MxnxrwK7MQE7sAbLrOVwsAorNf26sA67Nw37sBKLWNkwsRYL
        WORwsRpbQwm7sR47KBH7sR5bsCI7siFbshdLsiibsie7shKrsi77spqhATGLrjOb
        AjXLqzeLszmrqzuLAj3rsz/+awJBe6tDS7RFW6tHWwJJq7RLOwJNK6tPC7VRC6tT
        KwJVa7VXCwJZC69b+wFdq6pfC7ZhC6pj6wFla7ZnywFpi6truwFtS69vqwzCOrcV
        S5R2e7eLk7f5qjd8a5tq87c1OTiCS5B7W7hDibeIKw11u7jQ0LiO6wyQG7nMMLmU
        S7eKe7mVm7mai7mH27meS7igG7oIO7qDW7qmC5L8k7qqCz6sa7iu+7qJu7qy+7jR
        WruSe7u4u7m0u7u8G7u+2wzZE7yaybDEK7y6e7wGCrzKW7xj07yka63QmwxZNb38
        ua3We7rYm72tC0fcC7ve+72zi7Hia7toVb7PUL3oywtu6ru+utC+7uur8Wu+5Du/
        1Eux9uuq+Ju/7Lu//Pu+/vu/AjzABFzABnzACJzACrzADNzADvzAEBzBEjzBFFzB
        FnzBGJzBGrzBHNzBHvzBIBzCIjzCJFzCJnzCKJzCKrzCLNzCLvzCMBzDMjy2CQAA
        Ow==
        '''

root = tk.Tk()
app = Application(master=root)
app.mainloop()