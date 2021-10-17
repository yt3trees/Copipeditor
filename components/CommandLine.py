'''コマンドライン実行'''
import argparse
import os
import sys
from logging import getLogger, StreamHandler, FileHandler, basicConfig, DEBUG, INFO
import datetime

from . import Global
from . import CopyProcess

logger = getLogger(__name__)

class CommandLine:
    def __init__(self):
        # オブジェクト生成
        parser = argparse.ArgumentParser(description="ファイルをフォルダごとコピーするプログラムです。\
                                            コマンドライン引数を渡さずに実行した場合はGUIが起動します。", exit_on_error=False)
        # オプション引数
        parser.add_argument('--all', action = 'store_true', help="登録している全てのアイテムのコピーが実行されます。")
        parser.add_argument('--cp', nargs='*', type = str, help="コピー処理実行対象を複数指定できます。Ex)--copy red blue yellow")
        parser.add_argument('--bk', action = 'store_true', help = "ファイルをバックアップしたい場合はこの引数を追加してください。")
        parser.add_argument('--mv', action = 'store_true', help = "コピー元ファイルを削除したい場合はこの引数を追加してください。")
        parser.add_argument('--log', type = str, help="処理結果テキストの出力先を指定したい場合はパスを入力してください。デフォルトはスクリプトと同階層です。")
        self.args = parser.parse_args()

    def get_result(self):
        # --logに引数がある場合は結果出力テキストボックスの場所を指定
        if self.args.log:
            if not os.path.exists(self.args.log):
                print('パスが存在していません。' + self.args.log)
                sys.exit()
            resultPath = self.args.log
            resultText = resultPath + "./result.txt"
        else:
            resultPath = os.path.dirname(sys.argv[0])
            resultText = resultPath + "./result.txt"


        # 引数が渡された場合はresult.textを初期化
        if len(sys.argv) >= 2:
            with open(resultText, 'w') as f: print(str(datetime.date.today()) + " " + str(datetime.datetime.now().time())[0:5], file = f)

        return resultText

    def file_operation(self):
        try:
            self.bkFlg = self.args.bk
            self.delFlg = self.args.mv

            # 引数に--allと--cp両方ある場合は終了
            if self.args.all and self.args.cp:
                logger.info('--allか--cpのどちらかを指定してください。')
                sys.exit()

            # 引数に--allも--cpもない場合は終了
            if not self.args.all and not self.args.cp and len(sys.argv) >= 2:
                logger.info('--allもしくは--cpは必須です。')
                sys.exit()

            # --cpに引数がない場合は終了
            if not self.args.cp:
                if self.args.cp == []:
                    logger.info('--cpに値は必須です。')
                    sys.exit()

            # jsonファイル読み込みとコピー実行
            jsonOpe = Global.JsonOperation()
            if os.path.exists(Global.PARAM):
                jsonValues = jsonOpe.load_json('')
                i = 0
                items = {}
                for j in jsonValues.values():
                    if i == 0:
                        self.logFolder = jsonValues.get('logFolder')
                        i += 1
                    else:
                        if self.args.all or self.args.cp:
                            items[i] = {'id':j['id'],'from':j['from'],'to':j['to']}
                        i += 1
            else:
                logger.info('jsonファイルの読み込みに失敗しました。')

            # --allもしくは--cp
            if self.args.all or self.args.cp:
                self.itemId = []
                self.itemFrom = []
                self.itemTo = []

                # --cpの場合
                if self.args.cp:
                    logger.info('>>指定したアイテムが登録済みか比較します。')
                    logger.info('---------+----------------------------')
                    logger.info('比較結果\t指定アイテム  \t登録済みアイテム')
                    logger.info('---------+----------------------------')
                    for i in self.args.cp:
                        x = 1 # 登録済みアイテムリストの添字([0]はバックアップフォルダパス)
                        for sss in items:
                            if i == items[x]['id']: # 比較一致した場合は指定IDの比較をbreakして次のIDの比較に移る
                                logger.info('一致\t'+ i +  ' -> \t' + items[x]['id'])
                                self.itemId.append(items[x]['id'])
                                self.itemFrom.append(items[x]['from'])
                                self.itemTo.append(items[x]['to'])
                                x = 1
                                break
                            else: # 比較不一致の場合は指定IDはそのままで次の登録済みIDに移る
                                logger.info('不一致\t'+ i + ' -> \t' + items[x]['id'])
                                x += 1
                    logger.info('---------+----------------------------')

                # --allの場合
                if self.args.all:
                    x = 1
                    for i in items:
                        self.itemId.append(items[x]['id'])
                        self.itemFrom.append(items[x]['from'])
                        self.itemTo.append(items[x]['to'])
                        x += 1

                logger.info("■実行対象アイテム")
                if self.args.all:
                    x = 1
                    for i in self.itemId:
                        logger.info('-' + i + '     \t' + items[x]['from'] + ' -> ' + items[x]['to'])
                        x += 1
                if self.args.cp:
                    for i in self.itemId:
                        logger.info('-' + i)

                for f in self.itemFrom:
                    if not os.path.exists(f):
                        message = "パス'" + f + "'は存在しません。\n処理を中止します。"
                        logger.info('>>' + message.replace("\n",""))
                        sys.exit()
                for t in self.itemTo:
                    if not os.path.exists(t):
                        message = "パス'" + t + "'は存在しません。\n処理を中止します。"
                        logger.info('>>' + message.replace("\n",""))
                        sys.exit()

        except argparse.ArgumentError:
            logger.info('引数が正しくありません。--helpで引数の渡し方を確認してください。')
            sys.exit()

    def copy_command(self):
        today = str(datetime.date.today()).replace("-", "") # yyyymmdd
        time = str(datetime.datetime.now().time())[0:6].replace(":","")
        dateNow = today + time
        logFolderNow = self.logFolder + "/" + dateNow

        cp = CopyProcess.CopyProcess()
        cp.exec_copy(self.itemId, self.itemFrom, self.itemTo, logFolderNow, self.bkFlg, self.delFlg)


