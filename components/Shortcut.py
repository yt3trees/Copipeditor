class Shortcut:
    def define(self, page, obj, obj2):
        if page == "main": # メインページ
            obj.master.bind("<Return>", obj.tree.bind('<Double-1>')) # Enterキー
            obj.master.bind("<Control-n>", obj.addButt.bind("<Button-1>")) # 追加
            obj.master.bind("<Delete>",  obj.delButt.bind("<Button-1>")) # 削除
            obj.master.bind("<Control-a>", obj.allButt.bind("<Button-1>")) # 全選択
            obj.master.bind("<F5>", obj.button.bind("<Button-1>")) # 実行
            obj.master.bind("<Control-s>", obj.saveButt.bind("<Button-1>")) # 保存
            obj.master.bind("<k>", lambda c: obj2.move_up_item(obj.tree, "up")) # 上に並び替え
            obj.master.bind("<j>", lambda c: obj2.move_up_item(obj.tree, "down")) # 下に並び替え
            obj.master.bind("<Shift-Alt-K>", lambda c: obj2.copy_item(obj.tree, "up")) # アイテムを複製
            obj.master.bind("<Shift-Alt-J>", lambda c: obj2.copy_item(obj.tree, "down")) # アイテムを複製
            obj.master.bind("<Button-2>", lambda c: obj2.copy_item(obj.tree, "down")) # アイテムを複製
            # obj.master.bind("<Escape>", lambda c: self.tree.selection_remove(obj.tree.selection())) # 選択解除
            obj.master.bind("<space>", lambda c: obj2.check_item(obj.tree)) # チェック
            obj.master.bind("<Button-3>", lambda c: obj2.check_item(obj.tree)) # チェック

        if page == "entry": # 入力ページ
            obj.bind("<Escape>", lambda c: obj2.close_window(obj)) # サブメニューを閉じる
            obj.bind("<Return>", lambda e: obj2.update_then_destroy()) # 入力内容確定

        if page == "menu": # メニュー関連ページ
            obj.bind("<Escape>", lambda c: obj.destroy()) # サブメニューを閉じる
            obj.bind("<Return>", lambda e: obj.destroy()) # サブメニューを閉じる