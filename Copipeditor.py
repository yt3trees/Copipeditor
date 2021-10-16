import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mbox
import os
import sys
from tkinter import filedialog
import json
from typing import Text
import datetime
from ttkwidgets import CheckboxTreeview
import threading
import argparse

from components import Global
from components import TreeOperation
from components import EditWindow
from components import CopyProcess
from components import Menu
from components import Shortcut

class Application(tk.Frame):
    def __init__(self, master=None):
        # インスタンス化
        self.treeOpe = TreeOperation.TreeOperation()
        self.shortcut = Shortcut.Shortcut()
        self.menu = Menu.Menu()
        self.editWin = EditWindow.EditWindow()

        tk.Frame.__init__(self, master)
        self.pack(expand=1, fill=tk.BOTH, anchor=tk.NW)
        self.master.title("Copipeditor")
        Global.ww = self.master.winfo_screenwidth()
        Global.wh = self.master.winfo_screenheight()
        lw = 750 # self.master.winfo_width()
        lh = 314 # self.master.winfo_height()
        self.master.geometry(str(lw)+"x"+str(lh)+"+"+str(int(Global.ww/2-lw/2-10))+"+"+str(int(Global.wh/2-lh/2-15)) )
        self.master.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(data=Global.ICON))

        self.win = None # サブメニュー重複対策
        self.create_widgets()
        self.menu.create_menu(self)
        # jsonファイル読み込み
        try:
            if os.path.exists(Global.PARAM):
                jsonOpen = open(Global.PARAM,"r")
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

        self.tree.heading("#0",text="ID",command = lambda : self.treeOpe.all_select_item(self.tree))
        # self.tree.heading(1,text="ID")
        self.tree.heading(1,text="コピー元")
        self.tree.heading(2,text="コピー先")
        self.tree.column("#0",width=120)
        # self.tree.column(1,width=65)
        self.tree.column(1,width=290)
        self.tree.column(2,width=290)
        self.tree.bind('<Double-1>', lambda c: self.editWin.open_edit(self)) # ダブルクリック
        self.tree.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=5)

        self.addButt = tk.Button(self, text="追加", width=20)
        self.addButt.bind("<Button-1>", lambda c: self.treeOpe.insert_tree(self.tree))
        self.addButt.grid(row=2, column=0, sticky="E", pady=5)

        self.delButt = tk.Button(self, text = "削除", width=20, bg = Global.btColorDel)
        self.delButt.bind("<Button-1>", lambda c: self.treeOpe.delete_item(self.tree))
        self.delButt.grid(row=2, column=1, sticky="E")

        self.allButt = tk.Button(self, text="全選択/全解除", width=20)
        self.allButt.bind("<Button-1>", lambda c: self.treeOpe.all_select_item(self.tree))
        self.allButt.grid(row=2, column=2, sticky="E")

        self.button = tk.Button(self, text="実行", width=20, bg = Global.btColorOk) # TODO:コピー元削除制御
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
        self.settButt.bind("<Button-1>", lambda e: EditWindow.EditWindow.advanced_setting(self))
        self.settButt.place(x = 675, y = 236.5)

        self.kakushiLbl = tk.Label(self.win, text = "( ^_^)b", font=("メイリオ", "25"))
        self.kakushiLbl.place(x=1000,y=500)

        # ショートカット
        self.shortcut.define("main", self)

    def copy_callback(self):
        '''exec_copyを別スレッドで実行するための関数'''
        thread = threading.Thread(target=self.exec_copy)
        thread.start() # ここで止まらずすぐに呼び出し元にreturnする
        return "break"

    def exec_copy(self):
        try:
            if self.tree.get_checked() == []: # アイテムが1つも選択されていない場合
                mbox.showwarning("アラート", "実行対象を選択してください。")
                return "break"
            i = 0
            id = []
            fromPath = []
            toPath = []
            for item in self.tree.get_checked(): # 各パスの存在確認
                row_data = self.tree.item(item) # 行データの取得
                row_value = row_data['values'] # 列データの取得
                id.append(row_data['text'])
                fromPath.append(row_value[0])
                toPath.append(row_value[1])
                if not os.path.exists(fromPath[i]):
                    message = "パス'" + fromPath[i] + "'は存在しません。\n処理を中止します。"
                    mbox.showerror("エラー", message)
                    print (">>", message, sep = "")
                    return
                if not os.path.exists(toPath[i]):
                    message = "パス'" + toPath[i] + "'は存在しません。\n処理を中止します。"
                    mbox.showerror("エラー", message)
                    print (">>", message, sep = "")
                    return
                i += 1

            today = str(datetime.date.today()).replace("-", "") # yyyymmdd
            time = str(datetime.datetime.now().time())[0:6].replace(":","")
            dateNow = today + time

            delMsg = ""
            if self.checkDel_v.get() == True: # コピー元削除チェックボックスがオンの場合
                delMsg = "\n※コピー後元のファイルは削除されます。"

            msbox = mbox.askokcancel("確認", "コピーを実行します。" + delMsg)
            if msbox == True: # OKボタン押下
                logFolderNow = self.bkEnt.get()+ "/" + dateNow
                if self.bkEnt.get() != "バックアップ無し": bkFlg = True
                else: bkFlg = False
                delFlg = self.checkDel_v.get()

                cp = CopyProcess.CopyProcess()
                cp.exec_copy(id, fromPath, toPath, logFolderNow, bkFlg, delFlg)
            else:
                return "break"
            return "break"

        except Exception as e:
            self.error_message(e)

    def save_item(self):
        '''アイテムの保存'''
        msbox = mbox.askokcancel("確認", "設定を保存します。")
        try:
            if msbox == True:
                self.tree.selection_set(self.tree.get_children())
                selected_items = self.tree.selection() # 行データの取得

                i = 0
                if self.check_v.get() == True or self.bkFolderPathBack==None:
                    a = {'logFolder':self.bkEnt.get()}
                else:
                    a = {'logFolder':self.bkFolderPathBack}
                for item in selected_items:
                    row_data = self.tree.item(item)
                    row_value = row_data['values']

                    if row_data['text'] == '':
                        raise ValueError("IDが入力されていないデータが存在します。")

                    a[i] = {'id':row_data['text'],'from':row_value[0],'to':row_value[1]}
                    i += 1

                with open(Global.PARAM, 'w') as f:
                    json.dump(a, f, indent=4, ensure_ascii=False)

                self.tree.selection_remove(self.tree.selection())
                mbox.showinfo('確認', '保存しました。')
            return "break"
        except Exception as e:
            self.error_message(e)

    def error_message(self, message):
        '''エラーメッセージ表示'''
        msg = "エラーが発生しました。\n" + str(message)
        mbox.showerror("Error!", msg)

    def change_readonly(self, var, ent):
        '''バックアップフォルダパスの書き込み許可切り替え'''
        if var.get() == False:
            ent.configure(state='normal')
            ent.delete(0,tk.END)
            ent.insert(tk.END, self.bkEntValue)
        elif var.get() == True:
            self.bkEntValue = ent.get()
            ent.delete(0,tk.END)
            self.bkFolderPathBack = self.bkEntValue
            ent.insert(tk.END, "バックアップ無し")
            ent.configure(state='readonly')
# endregion
    def folder_dialog(self,obj):
        '''フォルダ選択ダイアログの起動'''
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

# endregion

# regionコマンド実行
# オブジェクト生成
parser = argparse.ArgumentParser(description="ファイルをフォルダごとコピーするプログラムです。\
                                    コマンドライン引数を渡さずに実行した場合はGUIが起動します。")
# オプション引数
parser.add_argument('--all', action = 'store_true', help="登録している全てのアイテムのコピーが実行されます。")
parser.add_argument('--copy', nargs='*', type = str, help="コピー処理実行対象を複数指定できます。Ex)--copy red blue yellow")
#parser.add_argument('--log', type = str, help="処理結果のテキストファイルを出力したい場合は出力先フォルダを指定してください。")
args = parser.parse_args()
if args.copy != None:
    print("実行対象アイテム")
    for i in args.copy:
        print('>',i)
# endregion

# 引数がない場合はGUI起動
if len(sys.argv) <= 1:
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()