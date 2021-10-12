import sys
from cx_Freeze import setup, Executable

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'
# Winデスクトップ出ない場合「CUI」の場合はif文をコメントアウト

exe = Executable(script = "Copipeditor.py", base= base, icon='icon/copytool.ico')
# "test.py"にはexe化するファイルの名前を記載。

setup(name = 'Copipeditor',
    version = '1.0',
    description = 'copy tool',
    executables = [exe])