echo off
echo %~dp0
echo ���O��pip install cx_Freeze��cs_Freeze���C���X�g�[�����Ă��������B
echo build�t�H���_����exe���i�[����܂��B
python setup.py build
echo ���̑��̃t�@�C�����܂Ƃ߂�app�Ɋi�[���܂��B
if exist .\app\Copipeditor\Copipeditor.exe (
    echo �㏑�����܂��B
    echo A | xcopy .\build\exe.win-amd64-3.9 .\app\Copipeditor /S
) else (
    echo �V�K�ŃR�s�[���܂��B
    echo D | xcopy .\build\exe.win-amd64-3.9 .\app\Copipeditor /S
)
rem echo A | xcopy .\script .\app\Copipeditor\script /S
rem echo A | xcopy .\script\run_�X�^�[�g���j���[�ɒǉ�.bat .\app\Copipeditor /S
if exist .\app\Copipeditor\script (
    echo �㏑�����܂��B
    echo A | xcopy .\script .\app\Copipeditor\script /S
) else (
    echo �V�K�ŃR�s�[���܂��B
    echo D | xcopy .\script .\app\Copipeditor\script /S
)
pause