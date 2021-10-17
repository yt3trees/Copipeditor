import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mbox
import os
import sys
from tkinter import filedialog
from typing import Text
import datetime
import threading
from logging import getLogger, StreamHandler, FileHandler, basicConfig, DEBUG, INFO

from components import Global
from components import MainWindow
from components import SubWindow
from components import TreeOperation
from components import CopyProcess
from components import Menu
from components import Shortcut
from components import CommandLine

if len(sys.argv) <= 1: # GUI実行時の出力結果テキスト指定
    resultPath = os.path.dirname(sys.argv[0])
    resultText = resultPath + "./result.txt"
else:
    # コマンドライン実行インタンス生成、出力結果テキスト指定
    cl = CommandLine.CommandLine()
    resultText = cl.get_result()

# ロギング
logger = getLogger(__name__)
stream_handler = StreamHandler()
stream_handler.setLevel(INFO)
file_handler = FileHandler(resultText)
file_handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.propagate = False
basicConfig(level = DEBUG, handlers = [stream_handler, file_handler])

# コピー実行
if len(sys.argv) >= 2:
    cl.file_operation()
    cl.copy_command()

class Application(tk.Frame):
    def __init__(self, master=None):
        # インスタンス化
        self.treeOpe = TreeOperation.TreeOperation()
        self.shortcut = Shortcut.Shortcut()
        self.menu = Menu.Menu()
        self.subWin = SubWindow.SubWindow()

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
        self.mainWin = MainWindow.MainWindow(self) # メインウィンドウ生成
        self.menu.create_menu(self)

        # jsonファイル読み込み
        self.jsonOpe = Global.JsonOperation()
        if os.path.exists(Global.PARAM):
            jsonValues = self.jsonOpe.load_json(self)
            i = 0
            for j in jsonValues.values():
                if i == 0:
                    self.bkEnt.insert(tk.END, jsonValues.get('logFolder'))
                else:
                    self.tree.insert("", "end", iid=j['id'], text=j['id'], values=( j['from'], j['to']))
                i += 1

    def copy_callback(self):
        '''exec_copyを別スレッドで実行するための関数'''
        # 実行結果テキスト
        with open(resultText, 'w') as f: print(str(datetime.date.today()) + " " + str(datetime.datetime.now().time())[0:5], file = f)
        thread = threading.Thread(target=self.exec_copy)
        thread.start() # ここで止まらずすぐに呼び出し元にreturnする
        return "break"

    def exec_copy(self):
        try:
            if self.tree.get_checked() == []: # アイテムが1つも選択されていない場合
                mbox.showwarning("アラート", "実行対象を選択してください。")
                return "break"

            today = str(datetime.date.today()).replace("-", "") # yyyymmdd
            time = str(datetime.datetime.now().time())[0:6].replace(":","")
            dateNow = today + time
            logFolderNow = self.bkEnt.get()+ "/" + dateNow
            i = 0
            id = []
            fromPath = []
            toPath = []
            # 各パスの存在確認
            for item in self.tree.get_checked():
                row_data = self.tree.item(item) # 行データの取得
                row_value = row_data['values'] # 列データの取得
                id.append(row_data['text'])
                fromPath.append(row_value[0])
                toPath.append(row_value[1])
                if not os.path.exists(fromPath[i]):
                    message = "パス'" + fromPath[i] + "'は存在しません。\n処理を中止します。"
                    mbox.showerror("エラー", message)
                    logger.info(message.replace("\n",""))
                    return
                if not os.path.exists(toPath[i]):
                    message = "パス'" + toPath[i] + "'は存在しません。\n処理を中止します。"
                    mbox.showerror("エラー" + message)
                    logger.info(message.replace("\n",""))
                    return
                i += 1

            # コピー元削除チェックボックスがオンの場合に確認ダイアログのメッセージ追加
            addMsg = ""
            if self.checkDel_v.get() == True:
                addMsg += "\n※コピー後元のファイルは削除"
                delFlg = True
            else:
                delFlg = False

            # バックアップ実行可否フラグ
            if self.check_v.get() == True:
                bkFlg = True
            else:
                addMsg += "\n※バックアップ無し"
                bkFlg = False

            # 確認ダイアログ
            msbox = mbox.askokcancel("確認", "コピーを実行します。" + addMsg)
            if msbox == True: # OKボタン押下
                # コピー処理実行
                cp = CopyProcess.CopyProcess()
                cp.exec_copy(id, fromPath, toPath, logFolderNow, bkFlg, delFlg)
                mbox.showinfo("アラート", "処理完了しました。")
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
                    aaa = {'logFolder':self.bkEnt.get()}
                else:
                    aaa = {'logFolder':self.bkFolderPathBack}
                for item in selected_items:
                    row_data = self.tree.item(item)
                    row_value = row_data['values']

                    if row_data['text'] == '':
                        raise ValueError("IDが入力されていないデータが存在します。")

                    aaa[i] = {'id':row_data['text'],'from':row_value[0],'to':row_value[1]}
                    i += 1

                with open(Global.PARAM, 'w') as fff:
                    self.jsonOpe.save_json(aaa, fff, 4, False) # json.dump(aaa, fff, indent=4, ensure_ascii=False)

                self.tree.selection_remove(self.tree.selection())
                mbox.showinfo('確認', '保存しました。')
            return "break"
        except Exception as e:
            self.error_message(e)

    def error_message(self, message):
        '''エラーメッセージ表示'''
        msg = "エラーが発生しました。\n" + str(message)
        mbox.showerror("Error!", msg)
        logger.info(message)

    def folder_dialog(self,obj):
        '''フォルダ選択ダイアログの起動'''
        try:
            dir = obj.get()
            logger.info(dir)
            fld = filedialog.askdirectory(initialdir = dir)
            if fld != "":
                obj.delete(0,tk.END)
                obj.insert(tk.END,fld)
            return "break"
        except Exception as e:
            self.error_message(e)

# 引数がない場合はGUI起動
if len(sys.argv) <= 1:
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()