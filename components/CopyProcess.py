'''
コピー処理実行モジュール
'''

import tkinter as tk
import tkinter.ttk as ttk
import os
from tkinter import messagebox as mbox
import shutil
from distutils import dir_util
import glob
from . import Global

class CopyProcess:
    def exec_copy(self, id:list, fromPath:list, toPath:list, logFolderNow:str, bkFlg:bool, delFlg:bool):
        '''
        コピー処理の実行
        Args:
            id (list): 処理するアイテムのID
            fromPath (list): 処理するアイテムのコピー元フォルダパス
            toPath (list): 処理するアイテムのコピー先フォルダパス
            logFolderNow (str): バックアップ出力先フォルダパス
            bkFlg (bool): バックアップ実行可否フラグ
            delFlg (bool): コピー元ファイル削除可否フラグ
        '''
        try:
            self.progress_bar("start") # プログレスバー表示
            selected_items = id # 行データの取得
            print(">>コピー処理を開始します。\n■実行対象:", selected_items)

            x = 0
            for item in selected_items:
                print("\n----------\n■処理アイテム:", item)
                # フォルダ生成
                logFolderNowID = logFolderNow + "_" + id[x]
                logFolderNowFrom = logFolderNowID + "/" + "After"
                logFolderNowTo = logFolderNowID + "/" + "Before"
                if bkFlg == True:
                    if not os.path.exists(logFolderNowFrom):
                        os.makedirs(logFolderNowFrom)
                    if not os.path.exists(logFolderNowTo):
                        os.makedirs(logFolderNowTo)
                os.chdir(toPath[x]) # toフォルダに移動

                if os.path.exists(fromPath[x]):
                    searchPath = fromPath[x] + "/**/*"
                    i = []
                    files = ([p for p in glob.glob(searchPath, recursive=True)
                        if os.path.isfile(p)]) # コピー元ファイル一覧取得

                    # コピー先重複ファイルバックアップ処理
                    for file in files:
                        if bkFlg == True:
                            print("\n", file, "から", sep = "") # コピー元ファイル名
                            fileAfter = file.replace(fromPath[x], toPath[x]) # コピー先ファイル存在確認用文字列生成
                            print(fileAfter, "にコピーします。") # コピー先ファイル名
                            if os.path.exists(fileAfter):
                                toFile = fileAfter.replace(toPath[x], "")
                                logFolderNowToFile = logFolderNowTo + "/" + toFile[1:]
                                toFile = "./" + toFile
                                if not os.path.exists(os.path.dirname(logFolderNowToFile)):
                                    os.makedirs(os.path.dirname(logFolderNowToFile))
                                shutil.copy2(toFile, logFolderNowToFile)
                                print ("コピー先重複ファイルを",logFolderNowToFile,"にコピーしました。")

                    if bkFlg == True:
                        dir_util.copy_tree(fromPath[x], logFolderNowFrom) # コピー元ファイルをバックアップフォルダにコピー
                    dir_util.copy_tree(fromPath[x], toPath[x])
                    if delFlg == True: # コピー元削除チェックボックスがオンの場合
                        self.delete_from_files(fromPath[x])
                        print ("\n>>コピー元ファイルを削除しました。")
                    if not files:
                        print ("コピー元にファイルが存在していません。")
                    else:
                        print ('\n>>ファイルをコピーしました。',fromPath[x], "->" ,toPath[x])
                    dir_util._path_created = {} # キャッシュをクリア
                    x += 1
                else:
                    message = "パス'" + fromPath[x] + "'は存在しません。"
                    mbox.showerror("エラー", message)
                    x += 1
                    return "break"
            self.progress_bar("stop") # プログレスバー終了
            mbox.showinfo("アラート", "処理完了しました。")
            print ("\n>>処理完了しました。")
        except Exception as e:
            self.error_message(e)
            print ("処理を中止しました。\n", e)
            self.progress_bar("stop") # プログレスバー終了

    def progress_bar(self, param):
        if param == "start":
            self.winbar = tk.Toplevel()
            lw = 200
            lh = 45
            self.winbar.geometry(str(lw)+"x"+str(lh)+"+"+str(int(Global.ww/2-lw/2-10))+"+"+str(int(Global.wh/2-lh/2-15)))
            self.winbar.title("コピー中")
            self.winbar.attributes("-toolwindow", True)
            self.winbar.grab_set()
            self.winbar.focus_set()
            self.winbar.Lbl = tk.Label(self.winbar, text = "コピー中...")
            self.winbar.Lbl.pack()
            self.winbar.pb = ttk.Progressbar(self.winbar, mode="indeterminate",length="180") #非確定的モード
            self.winbar.pb.start()
            self.winbar.pb.pack()
            return self.winbar.pb

        elif param == "stop":
            self.winbar.destroy()

    def delete_from_files(self, path):
        shutil.rmtree(path)
        os.mkdir(path)
        return "break"

    def error_message(self, message):
        msg = "エラーが発生しました。\n" + str(message)
        mbox.showerror("Error!", msg)