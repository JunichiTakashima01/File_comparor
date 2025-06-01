
"""
Fast duplicate file finder.
Usage: duplicates.py <folder> [<folder>...]
Based on https://stackoverflow.com/a/36113168/300783
Modified for Python3 with some small code improvements.
"""
import os
import sys
import hashlib
from collections import defaultdict
from pathlib import Path
import shutil as st
import tkinter as tk
from tkinter import scrolledtext, ttk


Move = False
Main_Path = ''
Destination = ''


def chunk_reader(fobj, chunk_size=1024):
    """ Generator that reads a file in chunks of bytes """
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash_algo=hashlib.sha1):
    hashobj = hash_algo()
    with open(filename, "rb") as f:
        if first_chunk_only:
            hashobj.update(f.read(1024))
        else:
            for chunk in chunk_reader(f):
                hashobj.update(chunk)
    return hashobj.digest()


def check_for_duplicates(paths):
    files_by_size = defaultdict(list)
    files_by_small_hash = defaultdict(list)
    files_by_full_hash = dict()

    for path in paths:
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                try:
                    # if the target is a symlink (soft one), this will
                    # dereference it - change the value to the actual target file
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                except OSError:
                    # not accessible (permissions, etc) - pass on
                    continue
                files_by_size[file_size].append(full_path)

    # For all files with the same file size, get their hash on the first 1024 bytes
    for file_size, files in files_by_size.items():
        if len(files) < 2:
            continue  # this file size is unique, no need to spend cpu cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
            except OSError:
                # the file access might've changed till the exec point got here
                continue
            files_by_small_hash[(file_size, small_hash)].append(filename)

    # For all files with the hash on the first 1024 bytes, get their hash on the full
    # file - collisions will be duplicates
    for files in files_by_small_hash.values():
        if len(files) < 2:
            # the hash of the first 1k bytes is unique -> skip this file
            continue
        for filename in files:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
            except OSError:
                # the file access might've changed till the exec point got here
                continue

            if full_hash in files_by_full_hash:
                duplicate = files_by_full_hash[full_hash]
                print("Duplicate found:\n - %s\n - %s" % (filename, duplicate))
                if Move == True:
                    pf = Path(filename)
                    pd = Path(duplicate)
                    if pf.exists() == False or pd.exists() == False:
                        pass
                    elif Path(Main_Path) in pd.parents:
                        if Path(Main_Path) not in pf.parents:
                            determine_and_move(pf, pd)
                        
                    elif Path(Main_Path) in pf.parents:
                        files_by_full_hash[full_hash] = filename
                        determine_and_move(pd, pf)
                    else:
                        determine_and_move(pf, pd)
                    
            else:
                files_by_full_hash[full_hash] = filename
                

def check_for_duplicates_for_tkinter(path, result_window : scrolledtext.ScrolledText): 
    files_by_size = defaultdict(list)
    files_by_small_hash = defaultdict(list)
    files_by_full_hash = dict()

    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                # if the target is a symlink (soft one), this will
                # dereference it - change the value to the actual target file
                full_path = os.path.realpath(full_path)
                file_size = os.path.getsize(full_path)
            except OSError:
                # not accessible (permissions, etc) - pass on
                continue
            files_by_size[file_size].append(full_path)

    # For all files with the same file size, get their hash on the first 1024 bytes
    for file_size, files in files_by_size.items():
        if len(files) < 2:
            continue  # this file size is unique, no need to spend cpu cycles on it

        for filename in files:
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
            except OSError:
                # the file access might've changed till the exec point got here
                continue
            files_by_small_hash[(file_size, small_hash)].append(filename)

    # For all files with the hash on the first 1024 bytes, get their hash on the full
    # file - collisions will be duplicates
    for files in files_by_small_hash.values():
        if len(files) < 2:
            # the hash of the first 1k bytes is unique -> skip this file
            continue
        for filename in files:
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
            except OSError:
                # the file access might've changed till the exec point got here
                continue

            if full_hash in files_by_full_hash:
                duplicate = files_by_full_hash[full_hash]
                #print("Duplicate found:\n - %s\n - %s" % (filename, duplicate))
                result_window.config(state='normal')
                result_window.insert(tk.END, "Duplicate found:\n - %s\n - %s\n\n" % (filename, duplicate))
                result_window.see(tk.END)
                result_window.config(state='disabled')
                
                
                # if Move == True:
                #     pf = Path(filename)
                #     pd = Path(duplicate)
                #     if pf.exists() == False or pd.exists() == False:
                #         pass
                #     elif Path(Main_Path) in pd.parents:
                #         if Path(Main_Path) not in pf.parents:
                #             determine_and_move(pf, pd)
                        
                #     elif Path(Main_Path) in pf.parents:
                #         files_by_full_hash[full_hash] = filename
                #         determine_and_move(pd, pf)
                #     else:
                #         determine_and_move(pf, pd)
                    
            else:
                files_by_full_hash[full_hash] = filename


def determine_and_move(filename, file2) -> None:
    print('Start')
    if filename.exists() and file2.exists():
        adding = 0
        str_adding = ''
        while True:
            if (Destination / (filename.stem + str_adding + filename.suffix)).exists():
                adding += 1
            else:
                break
            if adding == 0:
                str_adding = ''
            else:
                str_adding = f'({adding})'
        d = Destination / (filename.stem + str_adding + filename.suffix)
        st.move(filename, d)
        if Destination != '':
            global File
            File.writelines(f'From    : {filename}\nMove to : {d}\nDup with: {file2}\n\n')
        print(f'Successfully moved {filename}\n')
                
def pre_setting():
    move = input('Want to move the files? Nothing for No:')
    if move != '':
        global Move
        Move = True
    if Move == True:
        global Main_Path # Can't find a way to let it work properly now
        Main_Path  = input('Set the main path, Nothing for no main path:')
        global Destination
        while True:
            Destination = input('Set Destination:')
            if Destination == '':
                break #Make it become the path that combine the path to search and dup
                #print('Not Nothing')
                #continue
            Destination = Path(Destination)
            if Destination.is_dir():
                break
            print('Enter valid path')
        input(f'Confirm: Move = {Move}\nDestination = {Destination}\nMain path = {Main_Path}')

def log_file_creating() -> 'file':
    adding = 0
    str_adding = ''
    while True:
        if (Destination / ('log' + str_adding + '.txt')).exists():
            adding += 1
        else:
            break
        if adding == 0:
            str_adding = ''
        else:
            str_adding = f'({adding})'
    return (Destination / ('log' + str_adding + '.txt'))
       

if __name__ == "__main__":
    pre_setting()
    paths = [Path(x) for x in input('Path(use comma to separate different paths):').split(',') if x != '']
    if len(paths) == 0 or paths[0] == '':
        print("No empty path")
        input()
        quit()
    if Destination == '':
        
        Destination = paths[0] / 'dup'
        if Destination.exists() != True:
            Destination.mkdir()
    try:
        if Destination != '':
            path = log_file_creating()
            global File
            File = open(path, 'w', encoding = 'utf-8')
            File.writelines('Duplicate File:\n\n')
            File.flush()
        for i in range(len(paths)):
            paths[i] = str(paths[i])
        if paths != []:
            check_for_duplicates(paths)
    except Exception as e:
        print(f'Error:\n{e}')
    finally:
        if Destination != '' and File != None:
            File.close()
        
        
    print('DONE')
    input()
    #if sys.argv[1:]:
    #    check_for_duplicates(sys.argv[1:])
    #    print('DONE')
    #else:
    #    print("Usage: %s <folder> [<folder>...]" % sys.argv[0])
