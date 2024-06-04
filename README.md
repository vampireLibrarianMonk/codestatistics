Codebase File Generator and Statistics
This repository contains two Python scripts: create_random_files.py and code_statistics.py. These scripts are designed to generate random files and subdirectories with random content and then analyze the generated files to provide statistics.

Prerequisites
Python 3.9.7
Setup
Clone the repository:
```
git clone https://github.com/yourusername/repository.git
cd repository
```

Ensure you have Python 3.9.7 installed. You can check your Python version by running:
```
python --version
```

Usage
File Generator: create_random_files.py
This script generates random files and subdirectories with random content.

Arguments
parent_directory: The directory where subdirectories and files will be generated.
num_subdirs: The number of subdirectories to create.
num_files: The number of files to create in each subdirectory.
max_depth: The maximum depth of nested subdirectories.
Running the Script
```
python create_random_files.py <parent_directory> <num_subdirs> <num_files> <max_depth>
```

Example
```
python create_random_files.py ./test_directory 5 10 3
```

This command will create 5 subdirectories with up to 10 files in each, nested up to 3 levels deep, within the test_directory.

Code Statistics: code_statistics.py
This script analyzes the generated files and provides statistics on the files and their contents.

Arguments
search_directory: The directory containing the files and subdirectories to be analyzed.
Running the Script
```
python code_statistics.py <search_directory>
```

Example
```
python code_statistics.py ./test_directory
```

This command will analyze the contents of test_directory and produce a report.

Sample Output
File Generator Output
The script create_random_files.py generates a generation_statistics.txt file with the following structure:

```
Parent directory: ./test_directory
Number of subdirectories: 5
Number of files per subdirectory: 10
Maximum subdirectory depth: 3

Total subdirectories created: 12
Total files created: 50
Total lines of code generated: 750

Files of each type created:
.cpp: 10
.h: 10
.js: 10
.py: 10
.ts: 10

Code statistics:
.cpp: 150 lines (20.00%)
.h: 150 lines (20.00%)
.js: 150 lines (20.00%)
.py: 150 lines (20.00%)
.ts: 150 lines (20.00%)
```

Code Statistics Output
The script code_statistics.py generates a codebase_report.txt file with the following structure:

```
Total archives found: 5
Archives by type:
.tar: 1
.tar.gz: 2
.zip: 2

Total files found: 50
Total lines of code found: 750

Files of each type found:
.cpp: 10
.h: 10
.js: 10
.py: 10
.ts: 10

Language statistics:
.cpp: 150 lines (20.00%)
.h: 150 lines (20.00%)
.js: 150 lines (20.00%)
.py: 150 lines (20.00%)
.ts: 150 lines (20.00%)
```

Notes
Ensure you have the necessary permissions to create and modify files in the specified directories.
The scripts were tested with Python 3.9.7.