class TreeOperation:
    # 新規追加
    def insert_tree(self, obj): 
        i = 0
        m = ""
        num = len(obj.get_children()) # 全アイテム数
        print("-----")
        while True: # breakするまで永遠ループ
            print(">>",m,"ループ処理開始",sep="")
            for item in obj.get_children():
                print('候補:',i,'重複チェック先:',obj.item(item)['text'])
                if i == obj.item(item)['text']: # IDが重複しているかチェック
                    print("iid一致データあり\n")
                    i = i + 1 # 重複した場合は
                    m = "再"
                    break
                m = ""
            if m == "":
                break
        print("ID:「", i, "」で作成しました。", sep="")
        obj.insert("", "end", iid=i, text=i, value=("","",""))
        return "break"

    # チェックオンオフ判定
    def check_item(self, obj):
        for item in obj.selection():
            if obj.tag_has('unchecked', item):
                obj.change_state(item, 'checked')
            else:
                obj.change_state(item, 'unchecked')

    # アイテム削除
    def delete_item(self, obj):
        selected_items = obj.get_checked() # 行データの取得
        for item in selected_items:
            obj.delete(item)

    # 全選択/全解除
    def all_select_item(self, obj):
        allItem = obj.get_children()
        checkedItem = obj.get_checked()
        if len(allItem) != len(checkedItem): # 選択されていないアイテムが1つでもあれば全選択
            for i in allItem:
                obj.change_state(i, 'checked')
        else:
            for i in allItem:
                obj.change_state(i, 'unchecked')

    # アイテム位置移動
    def move_up_item(self, obj, m):
        if m == "up":
            cal = 1
        elif m == "down":
            i = len(obj.get_checked()) # 選択アイテム数
            cal = -i # 複数選択の場合、複数選択分まとめて移動
        for selected_item in obj.get_checked():
            obj.move(selected_item, obj.parent(selected_item), obj.index(selected_item) - cal)

    # アイテム複製
    def copy_item(self, obj, m):
        if m == "up":
            cal = 0
        elif m == "down":
            cal = len(obj.get_checked())
        a = 0
        for item in obj.get_checked() :
            idx = obj.index(item)
            if m == "up" and a > 0:
                idx = idx -a
            itemValue = obj.item(item)['values']
            obj.insert('', idx+cal, values = (itemValue))
            a += 1
        return True