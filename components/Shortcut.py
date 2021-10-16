'''
ショートカットキー定義モジュール
'''
from . import SubWindow
from logging import getLogger, StreamHandler, DEBUG, FileHandler
logger = getLogger(__name__)
class Shortcut:
    def define(self, page, obj):
        '''
        ショートカットキー定義
        Args:
            page : ショートカットを設定するウィンドウ
            obj : 呼び出し元のインスタンス
        '''
        if page == "main": # メインページ
            obj.master.bind("<Return>", obj.tree.bind('<Double-1>')) # Enterキー
            obj.master.bind("<Control-n>", obj.addButt.bind("<Button-1>")) # 追加
            obj.master.bind("<Delete>",  obj.delButt.bind("<Button-1>")) # 削除
            obj.master.bind("<Control-a>", obj.allButt.bind("<Button-1>")) # 全選択
            obj.master.bind("<F5>", obj.button.bind("<Button-1>")) # 実行
            obj.master.bind("<Control-s>", obj.saveButt.bind("<Button-1>")) # 保存
            obj.master.bind("<k>", lambda c: obj.treeOpe.move_up_item(obj.tree, "up")) # 上に並び替え
            obj.master.bind("<j>", lambda c: obj.treeOpe.move_up_item(obj.tree, "down")) # 下に並び替え
            obj.master.bind("<Shift-Alt-K>", lambda c: obj.treeOpe.copy_item(obj.tree, "up")) # アイテムを複製
            obj.master.bind("<Shift-Alt-J>", lambda c: obj.treeOpe.copy_item(obj.tree, "down")) # アイテムを複製
            obj.master.bind("<Button-2>", lambda c: obj.treeOpe.copy_item(obj.tree, "down")) # アイテムを複製
            obj.master.bind("<space>", lambda c: obj.treeOpe.check_item(obj.tree)) # チェック
            obj.master.bind("<Button-3>", lambda c: obj.treeOpe.check_item(obj.tree)) # チェック

        if page == "entry": # 入力ページ
            sw = SubWindow.SubWindow()
            obj.win.bind("<Escape>", lambda c: sw.close_window(obj, obj.win)) # サブメニューを閉じる
            obj.win.bind("<Return>", lambda e: sw.update_then_destroy(obj)) # 入力内容確定

        if page == "menu": # メニュー関連ページ
            obj.winv.bind("<Escape>", lambda c: obj.winv.destroy()) # サブメニューを閉じる
            obj.winv.bind("<Return>", lambda e: obj.winv.destroy()) # サブメニューを閉じる