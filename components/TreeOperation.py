'''
Tree操作モジュール
'''
from logging import getLogger, StreamHandler, DEBUG, FileHandler
logger = getLogger(__name__)
class TreeOperation:
    def insert_tree(self, obj):
        '''新規追加'''
        i = 0
        m = ""
        num = len(obj.get_children()) # 全アイテム数
        logger.info("-----")
        while True: # breakするまで永遠ループ
            logger.info(">>",m,"ループ処理開始")
            for item in obj.get_children():
                logger.info('候補:' + str(i) + '重複チェック先:' + str(obj.item(item)['text']))
                if i == obj.item(item)['text']: # IDが重複しているかチェック
                    logger.info("iid一致データあり\n")
                    i = i + 1 # 重複した場合は
                    m = "再"
                    break
                m = ""
            if m == "":
                break
        logger.info("ID:「" + str(i) + "」で作成しました。")
        obj.insert("", "end", iid=i, text=i, value=("","",""))
        return "break"

    def check_item(self, obj):
        '''チェックボックスオンオフ切り替え'''
        for item in obj.selection():
            if obj.tag_has('unchecked', item):
                obj.change_state(item, 'checked')
            else:
                obj.change_state(item, 'unchecked')

    def delete_item(self, obj):
        '''アイテム削除'''
        selected_items = obj.get_checked() # 行データの取得
        for item in selected_items:
            obj.delete(item)

    def all_select_item(self, obj):
        '''全選択/全解除'''
        allItem = obj.get_children()
        checkedItem = obj.get_checked()
        if len(allItem) != len(checkedItem): # 選択されていないアイテムが1つでもあれば全選択
            for i in allItem:
                obj.change_state(i, 'checked')
        else:
            for i in allItem:
                obj.change_state(i, 'unchecked')

    def move_up_item(self, obj, m):
        '''アイテム位置移動'''
        if m == "up":
            cal = 1
        elif m == "down":
            i = len(obj.get_checked()) # 選択アイテム数
            cal = -i # 複数選択の場合、複数選択分まとめて移動
        for selected_item in obj.get_checked():
            obj.move(selected_item, obj.parent(selected_item), obj.index(selected_item) - cal)

    def copy_item(self, obj, m):
        '''アイテム複製'''
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