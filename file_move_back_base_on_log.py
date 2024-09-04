from pathlib import Path
import shutil

Log = Path(input('Path for the log file:'))
ReturnPath = Path(input('The path for the files to return:'))

rlog = 'Return Log:\n\n\n'

if (ReturnPath / 'move_back_log.txt').exists():
    raise

with open(Log, 'r', encoding = 'utf-8') as file:
    lines = file.readlines()
    for i, l in enumerate(lines):
        #l = l.encode('gbk').decode('utf-8')
        if l[:4] == 'From':
            if ReturnPath in Path(l[10:-1]).parents:
                dst = Path(l[10:-1])
                src = Path(lines[i+1][10:-1])#.encode('gbk').decode('utf-8'))
                shutil.move(src, dst)
                print('move back 1')
                rlog += f'From: {src}\nMove: {dst}\n\n'

            
with open(ReturnPath / 'move_back_log.txt', 'w',encoding = 'utf-8') as rlogf:
    rlogf.writelines(rlog)

input('Done')
