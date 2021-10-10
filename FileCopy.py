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
import webbrowser
import glob
import datetime
from ttkwidgets import CheckboxTreeview
import threading
# コンポーネント
from components import TreeOperation
from components import Shortcut
from components import Menu
from components import Global

# グローバル変数
VERSION = Global.VERSION
PARAM = Global.PARAM
SOURCE = Global.SOURCE
ICON = Global.ICON
btColorOk = Global.btColorOk
btColorDel = Global.btColorDel
btColorCan = Global.btColorCan

# クラス呼び出し
treeOpe = TreeOperation.TreeOperation()
shortcut = Shortcut.Shortcut()
menu = Menu.Menu()

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
        # iconfile = "icon\copytool.ico"
        # self.master.iconbitmap(default=iconfile)
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

# region---------------------------------------- メイン画面 ---------------------------------------- #
    def create_widgets(self):
        self.tree = CheckboxTreeview(self)
        self.tree["columns"] = (1,2)
        self.tree["show"] = "tree","headings"

        self.tree.heading("#0",text="ID",command = lambda : treeOpe.all_select_item(self.tree))
        # self.tree.heading(1,text="ID")
        self.tree.heading(1,text="コピー元")
        self.tree.heading(2,text="コピー先")
        self.tree.column("#0",width=120)
        # self.tree.column(1,width=65)
        self.tree.column(1,width=290)
        self.tree.column(2,width=290)
        self.tree.bind('<Double-1>', lambda c: self.on_double_click()) # ダブルクリック
        self.tree.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=5)

        self.addButt = tk.Button(self, text="追加", width=20)
        self.addButt.bind("<Button-1>", lambda c: treeOpe.insert_tree(self.tree))
        self.addButt.grid(row=2, column=0, sticky="E", pady=5)

        self.delButt = tk.Button(self, text = "削除", width=20, bg = btColorDel)
        self.delButt.bind("<Button-1>", lambda c: treeOpe.delete_item(self.tree))
        self.delButt.grid(row=2, column=1, sticky="E")

        self.allButt = tk.Button(self, text="全選択/全解除", width=20)
        self.allButt.bind("<Button-1>", lambda c: treeOpe.all_select_item(self.tree))
        self.allButt.grid(row=2, column=2, sticky="E")

        self.button = tk.Button(self, text="実行", width=20, bg = btColorOk) # TODO:コピー元削除制御
        self.button.bind("<Button-1>", lambda c: self.copy_callback())
        self.button.grid(row=2, column=3, sticky="E")

        self.saveButt = tk.Button(self, text = "保存", width=20)
        self.saveButt.bind("<Button-1>", lambda c: self.save_item())
        self.saveButt.grid(row=2, column=4, sticky="E")

        self.bkLbl = tk.Label(self, text = "バックアップフォルダ: ") # TODO:チェックボックスで使用可否制御
        self.bkLbl.grid(row = 1, column = 0)
        self.bkEnt = tk.Entry(self, width = 74)
        self.bkEnt.grid(row = 1, column = 1, sticky="W", pady=0, columnspan=3)
        self.bkFolderButt = tk.Button(self, text = "フォルダ", width = 9)
        self.bkFolderButt.bind("<Button-1>", lambda e: self.folder_dialog(self.bkEnt))
        self.bkFolderButt.grid(row = 1, column = 4, sticky = "W")

        self.check_v = tk.BooleanVar()
        self.check_v.set( True )
        self.bkEntValue = self.bkEnt.get()
        self.checkDel_v = tk.BooleanVar()
        self.checkDel_v.set( False )

        self.settButt = tk.Button(self, text = "詳細設定", width = 9)
        self.settButt.bind("<Button-1>", lambda e: self.advanced_setting())
        self.settButt.place(x = 675, y = 236.5)

        self.kakushiLbl = tk.Label(self.win, text = "( ^_^)b", font=("メイリオ", "25"))
        self.kakushiLbl.place(x=1000,y=500)

        # ショートカット
        shortcut.define("main", self, treeOpe)

    def copy_callback(self):
        self.progress_bar("start") # プログレスバー表示
        thread = threading.Thread(target=self.exec_copy)
        thread.start()
        return "break"

    def exec_copy(self):
        #os.chdir(os.path.dirname(sys.argv[0])) # カレントディレトリリセット
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
                    # フォルダ生成
                    logFolderNowID = logFolderNow + "_" + id
                    logFolderNowFrom = logFolderNowID + "/" + "After"
                    logFolderNowTo = logFolderNowID + "/" + "Before"
                    if self.bkEnt.get() != "バックアップ無し":
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

                        # コピー先重複ファイルバックアップ処理
                        for file in files:
                            if self.bkEnt.get() != "バックアップ無し":
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

                        if self.bkEnt.get() != "バックアップ無し":
                            dir_util.copy_tree(fromPath, logFolderNowFrom) # コピー元ファイルをバックアップフォルダにコピー
                        dir_util.copy_tree(fromPath, toPath)
                        if self.checkDel_v.get() == True: # コピー元削除チェックボックスがオンの場合
                            self.delete_from_files(fromPath)
                        print ('実行：',fromPath, "→" ,toPath)
                        dir_util._path_created = {} # キャッシュをクリア
                    else:
                        message = "パス'" + fromPath + "'は存在しません。"
                        mbox.showerror("エラー", message)
                        return "break"
                self.progress_bar("stop") # プログレスバー終了
                mbox.showinfo("アラート", "処理完了しました。")
            return "break"
        except Exception as e:
            self.error_message(e)
        finally:
            self.progress_bar("stop") # プログレスバー終了

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

    def error_message(self, message):
        msg = "エラーが発生しました。\n" + str(message)
        mbox.showerror("Error!", msg)

    def progress_bar(self, param):
        if param == "start":
            self.winbar = tk.Toplevel()
            lw = 200
            lh = 45
            self.winbar.geometry(str(lw)+"x"+str(lh)+"+"+str(int(self.ww/2-lw/2-10))+"+"+str(int(self.wh/2-lh/2-15)))
            self.winbar.title("コピー中")
            self.winbar.attributes("-toolwindow", True)
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

    def change_readonly(self, var, ent):
        if var.get() == False:
            ent.configure(state='normal')
            ent.delete(0,tk.END)
            ent.insert(tk.END, self.bkEntValue)
        elif var.get() == True:
            self.bkEntValue = ent.get()
            ent.delete(0,tk.END)
            ent.insert(tk.END, "バックアップ無し")
            ent.configure(state='readonly')

# endregion
# region---------------------------------------- サブ画面 ---------------------------------------- #
    def on_double_click(self): # https://try2explore.com/questions/jp/12101569
        if () == self.tree.selection(): return
        if self.win == None: # 重複して開かない
            self.win = tk.Toplevel()
            lw = 400
            lh = 100
            self.win.geometry(str(lw)+"x"+str(lh)+"+"+str(int(self.ww/2-lw/2-10))+"+"+str(int(self.wh/2-lh/2-15)))
            # self.win.geometry("400x100+975+600")
            self.win.title("Edit Entry")
            self.win.attributes("-toolwindow", True)
            # self.win.attributes("-topmost", True)
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

        # OKボタン
        self.okButt = tk.Button(self.win, text = "OK", bg = btColorOk, width = 5)
        self.okButt.bind("<Button-1>", lambda e: self.update_then_destroy())
        self.okButt.place(x = 263, y = 73)
        # Cancelボタン
        self.canButt = tk.Button(self.win, text = "Cancel", bg = btColorCan, width = 5)
        self.canButt.bind("<Button-1>", lambda c: self.close_window(self.win))
        self.canButt.place(x = 308, y = 73)
        # Deleteボタン
        self.delButt = tk.Button(self.win, text = "Delete", bg = btColorDel, width = 5)
        self.delButt.bind("<Button-1>", lambda c: self.tree.delete(self.tree.focus()) & self.close_window(self.win))
        self.delButt.place(x = 353, y = 73)

        # xボタン押下時の制御変更
        self.win.protocol('WM_DELETE_WINDOW', lambda : self.close_window(self.win))

        # ショートカット
        shortcut.define("entry", self.win, self)

    def update_then_destroy(self):
        if self.confirm_entry(self, self.col1Ent.get(), self.col2Ent.get(), self.col3Ent.get()):
            self.win.destroy()
            self.win = None

    def close_window(self,win): # サブメニュー重複対策
        win.destroy()
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

    def advanced_setting(self):
        self.winSet = tk.Toplevel()
        lw = 150
        lh = 110
        self.winSet.geometry(str(lw)+"x"+str(lh)+"+"+str(int(self.ww/2-lw/2-10))+"+"+str(int(self.wh/2-lh/2-15)))
        self.winSet.title("詳細設定")
        self.winSet.grab_set()
        self.winSet.attributes("-toolwindow", True)
        self.winSet.focus_set()

        self.winSet.checkBkFolder = tk.Checkbutton(self.winSet, text="バックアップする", variable=self.check_v)
        self.winSet.checkBkFolder.bind("<Button-1>", lambda e: self.change_readonly(self.check_v, self.bkEnt))
        self.winSet.checkBkFolder.grid(row = 0, column = 0, sticky = "W", pady=5, padx=15)
        self.winSet.checkDelFromFile = tk.Checkbutton(self.winSet, text="コピー元ファイル削除", variable=self.checkDel_v)
        self.winSet.checkDelFromFile.bind("<Button-1>", lambda e: self.change_setting_button_color(self.checkDel_v, self.settButt))
        self.winSet.checkDelFromFile.grid(row = 1, column = 0, sticky = "W", pady=5, padx=15)
        self.winSet.okButt = tk.Button(self.winSet, text = "OK", width=10)
        self.winSet.okButt.bind("<Button-1>", lambda c: self.winSet.destroy())
        self.winSet.okButt.place(x = lw/4, y = 80)

        self.winSet.bind("<Escape>", lambda c: self.close_window(self.winSet))
        return "break"

    def delete_from_files(self, path):
        shutil.rmtree(path)
        os.mkdir(path)
        return "break"

    def change_setting_button_color(self, var, btn):
        if var.get() == False:
            btn.configure(bg=btColorDel)
        elif var.get() == True:
            btn.configure(bg="#F0F0F0")

# endregion
# ---------------------------------------- メニュー画面 ---------------------------------------- #
    def create_menu(self):
        menu.create_menu(self, treeOpe, shortcut)
        #menu.open_version(self, shortcut)

root = tk.Tk()
app = Application(master=root)
app.mainloop()