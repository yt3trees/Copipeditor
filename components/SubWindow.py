'''
サブウィンドウ生成モジュール
'''
import tkinter as tk
from . import Global
from . import Shortcut
from logging import getLogger, StreamHandler, DEBUG, FileHandler
logger = getLogger(__name__)

sc = Shortcut.Shortcut()
class SubWindow:
    def open_edit(self, obj): # https://try2explore.com/questions/jp/12101569
        if () == obj.tree.selection(): return
        if obj.win == None: # 重複して開かない
            obj.win = tk.Toplevel()
            # lw = 400
            # lh = 100
            # obj.win.geometry("400x100+975+600")
            obj.win.title("Edit Entry")
            obj.win.attributes("-toolwindow", True)
            # obj.win.attributes("-topmost", True)
            obj.win.grab_set()
            obj.win.focus_set()

        # 行データの取得
        selected_items = obj.tree.selection()
        row_data = obj.tree.item(selected_items[0])

        # 列データの取得
        row_value = row_data['values']
        # title = row_value[0]
        title = row_data['text'] # id
        fromPath = row_value[0] # from
        toPath = row_value[1] # to

        obj.col1Lbl = tk.Label(obj.win, text = "ID: ", font = obj.deffont)# 一意になるように制限
        obj.col1Ent = tk.Entry(obj.win, width = 20, font = obj.deffont)
        obj.col1Ent.insert(0, title)
        obj.col1Lbl.grid(row = 0, column = 0)
        obj.col1Ent.grid(row = 0, column = 1, sticky="W")

        obj.col2Lbl = tk.Label(obj.win, text = "コピー元: ", font = obj.deffont)
        obj.col2Ent = tk.Entry(obj.win, width = 50, font = obj.deffont)
        obj.col2Ent.insert(0, fromPath)
        obj.col2Lbl.grid(row = 1, column = 0)
        obj.col2Ent.grid(row = 1, column = 1, columnspan = 3)

        obj.folderButt = tk.Button(obj.win, text = "フォルダ", width = 14, font = obj.deffont)
        obj.folderButt.bind("<Button-1>", lambda e: obj.folder_dialog(obj.col2Ent))
        obj.folderButt.grid(row = 1, column = 4, sticky = "W")

        obj.col3Lbl = tk.Label(obj.win, text = "コピー先: ", font = obj.deffont)
        obj.col3Ent = tk.Entry(obj.win, width = 50, font = obj.deffont)
        obj.col3Ent.insert(0, toPath)
        obj.col3Lbl.grid(row = 2, column = 0)
        obj.col3Ent.grid(row = 2, column = 1, columnspan = 3)

        obj.folder2Butt = tk.Button(obj.win, text = "フォルダ", width = 14, font = obj.deffont)
        obj.folder2Butt.bind("<Button-1>", lambda e: obj.folder_dialog(obj.col3Ent))
        obj.folder2Butt.grid(row = 2, column = 4, sticky = "W")

        # OKボタン
        obj.okButt = tk.Button(obj.win, text = "OK", bg = Global.btColorOk, width = 14, font = obj.deffont)
        obj.okButt.bind("<Button-1>", lambda e: self.update_then_destroy(obj))
        obj.okButt.grid(row=3, column=2, sticky="E")
        # obj.okButt.place(x = 263, y = 73)
        # Cancelボタン
        obj.canButt = tk.Button(obj.win, text = "Cancel", bg = Global.btColorCan, width = 14, font = obj.deffont)
        obj.canButt.bind("<Button-1>", lambda c: self.close_window(obj, obj.win))
        obj.canButt.grid(row=3, column=3, sticky="E")
        # obj.canButt.place(x = 308, y = 73)
        # Deleteボタン
        obj.delButt = tk.Button(obj.win, text = "Delete", bg = Global.btColorDel, width = 14, font = obj.deffont)
        obj.delButt.bind("<Button-1>", lambda c: self.delete_button(obj))
        obj.delButt.grid(row=3, column=4, sticky="E")
        # obj.delButt.place(x = 353, y = 73)

        # xボタン押下時の制御変更
        obj.win.protocol('WM_DELETE_WINDOW', lambda : self.close_window(obj, obj.win))

        # ショートカット
        sc.define("entry", obj)

        obj.win.update_idletasks()
        lw = obj.win.winfo_width()
        lh = obj.win.winfo_height()
        obj.win.geometry("+"+str(int(obj.ww/2-lw/2))+"+"+str(int(obj.wh/2-lh/2)))

    def delete_button(self, obj):
        '''アイテム削除'''
        obj.tree.delete(obj.tree.focus())
        self.close_window(obj, obj.win)

    def update_then_destroy(self, obj):
        '''編集情報の確定'''
        if self.confirm_entry(obj, obj.col1Ent.get(), obj.col2Ent.get(), obj.col3Ent.get()):
            obj.win.destroy()
            obj.win = None

    def confirm_entry(self, obj, entry1, entry2, entry3):
        '''アイテムを削除してインサート'''
        currInd = obj.tree.index(obj.tree.focus())
        self.delete_current_entry(obj)
        obj.tree.insert('', currInd, iid = entry1, text = entry1, values = (entry2, entry3))
        return True

    def delete_current_entry(self, obj):
        '''アイテム削除'''
        curr = obj.tree.focus()
        if '' == curr: return
        obj.tree.delete(curr)

    def close_window(self, obj, win):
        '''ウィンドウを閉じる(サブメニュー重複起動対策)'''
        win.destroy()
        obj.win = None
        return "break"

    def advanced_setting(self, obj):
        '''詳細設定を開く'''
        obj.winSet = tk.Toplevel()
        # lw = 150
        # lh = 110
        # obj.winSet.geometry("+"+str(int(Global.ww/2-lw/2-10))+"+"+str(int(Global.wh/2-lh/2-15)))
        obj.winSet.title("詳細設定")
        obj.winSet.grab_set()
        obj.winSet.attributes("-toolwindow", True)
        obj.winSet.focus_set()

        obj.winSet.checkBkFolder = tk.Checkbutton(obj.winSet, text="バックアップする", variable=obj.check_v, font = obj.deffont)
        obj.winSet.checkBkFolder.bind("<Button-1>", lambda e: self.change_readonly(obj, obj.check_v, obj.bkEnt))
        obj.winSet.checkBkFolder.grid(row = 0, column = 0, sticky = "W", pady=5, padx=15)
        obj.winSet.checkDelFromFile = tk.Checkbutton(obj.winSet, text="コピー元ファイル削除", variable=obj.checkDel_v, font = obj.deffont)
        obj.winSet.checkDelFromFile.bind("<Button-1>", lambda e: self.change_setting_button_color(obj.checkDel_v, obj.settButt))
        obj.winSet.checkDelFromFile.grid(row = 1, column = 0, sticky = "W", pady=5, padx=15)
        obj.winSet.okButt = tk.Button(obj.winSet, text = "OK", width=10, font = obj.deffont)
        obj.winSet.okButt.bind("<Button-1>", lambda c: obj.winSet.destroy())
        obj.winSet.okButt.grid(row = 2, column = 0)
        # obj.winSet.okButt.place(x = lw/4, y = 80)

        obj.winSet.bind("<Escape>", lambda c: self.close_window(obj, obj.winSet))

        obj.winSet.update_idletasks()
        lw = obj.winSet.winfo_width()
        lh = obj.winSet.winfo_height()
        obj.winSet.geometry("+"+str(int(obj.ww/2-lw/2))+"+"+str(int(obj.wh/2-lh/2)))

        return "break"

    def change_setting_button_color(self, var, btn):
        '''詳細設定ボタンの色変更'''
        if var.get() == False:
            btn.configure(bg=Global.btColorDel)
        elif var.get() == True:
            btn.configure(bg="#F0F0F0")

    def change_readonly(self, obj, var, ent):
        '''バックアップフォルダパスの書き込み許可切り替え'''
        if var.get() == False:
            ent.configure(state='normal')
            ent.delete(0,tk.END)
            ent.insert(tk.END, obj.bkEntValue)
        elif var.get() == True:
            obj.bkEntValue = ent.get()
            ent.delete(0,tk.END)
            obj.bkFolderPathBack = obj.bkEntValue
            ent.insert(tk.END, "バックアップ無し")
            ent.configure(state='readonly')