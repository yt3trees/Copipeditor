'''
メインウィンドウ生成モジュール
'''
import tkinter as tk
import tkinter.ttk as ttk
from ttkwidgets import CheckboxTreeview
from . import Global
from logging import getLogger, StreamHandler, DEBUG, FileHandler
logger = getLogger(__name__)
class MainWindow:
    def __init__(self, obj):
        style = ttk.Style()
        style.configure("Treeview.Heading", font = obj.deffont)
        style.configure("Treeview", font = obj.deffont)
        style.configure('Treeview', rowheight=30)
        obj.tree = CheckboxTreeview(obj)
        obj.tree["columns"] = (1,2)
        obj.tree["show"] = "tree","headings"

        obj.tree.heading("#0",text="ID",command = lambda : obj.treeOpe.all_select_item(obj.tree))
        # obj.tree.heading(1,text="ID")
        obj.tree.heading(1,text="コピー元")
        obj.tree.heading(2,text="コピー先")
        obj.tree.column("#0",width=120)
        # obj.tree.column(1,width=65)
        obj.tree.column(1,width=290)
        obj.tree.column(2,width=290)
        obj.tree.bind('<Double-1>', lambda c: obj.subWin.open_edit(obj)) # ダブルクリック
        obj.tree.grid(row=0, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=6)

        obj.addButt = tk.Button(obj, text="追加", width=20, font = obj.deffont)
        obj.addButt.bind("<Button-1>", lambda c: obj.treeOpe.insert_tree(obj.tree))
        obj.addButt.grid(row=2, column=0, sticky="E", pady=5)

        obj.delButt = tk.Button(obj, text = "削除", width=20, bg = Global.btColorDel, font = obj.deffont)
        obj.delButt.bind("<Button-1>", lambda c: obj.treeOpe.delete_item(obj.tree))
        obj.delButt.grid(row=2, column=1, sticky="E")

        obj.allButt = tk.Button(obj, text="全選択/全解除", width=20, font = obj.deffont)
        obj.allButt.bind("<Button-1>", lambda c: obj.treeOpe.all_select_item(obj.tree))
        obj.allButt.grid(row=2, column=2, sticky="E")

        obj.button = tk.Button(obj, text="実行", width=20, bg = Global.btColorOk, font = obj.deffont)
        obj.button.bind("<Button-1>", lambda c: obj.copy_callback())
        obj.button.grid(row=2, column=3, sticky="E")

        obj.saveButt = tk.Button(obj, text = "保存", width=20, font = obj.deffont)
        obj.saveButt.bind("<Button-1>", lambda c: obj.save_item())
        obj.saveButt.grid(row=2, column=4, sticky="E", columnspan = 2)

        obj.bkLbl = tk.Label(obj, text = "バックアップフォルダ: ", font = obj.deffont)
        obj.bkLbl.grid(row = 1, column = 0)
        obj.bkEnt = tk.Entry(obj, width = 60, font = obj.deffont)
        obj.bkEnt.grid(row = 1, column = 1, sticky="W", pady=0, columnspan = 3)
        obj.bkFolderButt = tk.Button(obj, text = "フォルダ", width = 9, font = obj.deffont)
        obj.bkFolderButt.bind("<Button-1>", lambda e: obj.folder_dialog(obj.bkEnt))
        obj.bkFolderButt.grid(row = 1, column = 4, sticky = "W")

        obj.check_v = tk.BooleanVar()
        obj.check_v.set( True )
        obj.bkEntValue = obj.bkEnt.get()
        obj.checkDel_v = tk.BooleanVar()
        obj.checkDel_v.set( False )

        obj.settButt = tk.Button(obj, text = "詳細設定", width = 9, font = obj.deffont)
        obj.settButt.bind("<Button-1>", lambda e: obj.subWin.advanced_setting(obj))
        obj.settButt.grid(row=1, column=5, sticky="E")
        # obj.settButt.place(x = 675, y = 236.5)

        obj.kakushiLbl = tk.Label(obj.win, text = "( ^_^)b", font=("メイリオ", "25"))
        obj.kakushiLbl.place(x=1000,y=500)

        # ショートカット
        obj.shortcut.define("main", obj)

        obj.update_idletasks()
        # lw = 750 # obj.master.winfo_width()
        lw = obj.master.winfo_width()
        # lh = 316 # obj.master.winfo_height()
        lh = obj.master.winfo_height()
        obj.master.geometry("+"+str(int(obj.ww/2-lw/2))+"+"+str(int(obj.wh/2-lh/2)))