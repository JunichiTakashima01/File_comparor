# File_comparer

Compare files using the hash of the file. To ensure speed, it will first record the hash of the first 1024 bytes of the file; if there is a match, it will compare the rest. 
It can also record the process into a log file with information about what is duplicated and what is moved to ensure it is revertable.
