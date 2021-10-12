echo off
echo %~dp0
echo 事前にpip install cx_Freezeでcs_Freezeをインストールしてください。
echo buildフォルダ内にexeが格納されます。
python setup.py build
echo その他のファイルをまとめてappに格納します。
if exist .\app\Copipeditor\Copipeditor.exe (
    echo 上書きします。
    echo A | xcopy .\build\exe.win-amd64-3.9 .\app\Copipeditor /S
) else (
    echo 新規でコピーします。
    echo D | xcopy .\build\exe.win-amd64-3.9 .\app\Copipeditor /S
)
rem echo A | xcopy .\script .\app\Copipeditor\script /S
rem echo A | xcopy .\script\run_スタートメニューに追加.bat .\app\Copipeditor /S
if exist .\app\Copipeditor\script (
    echo 上書きします。
    echo A | xcopy .\script .\app\Copipeditor\script /S
) else (
    echo 新規でコピーします。
    echo D | xcopy .\script .\app\Copipeditor\script /S
)
pause