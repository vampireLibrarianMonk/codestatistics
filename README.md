Project Overview
This project contains three Python scripts designed for various purposes related to file and code analysis. Below are the descriptions and usage instructions for each script:

1. code_statistics.py
   This script analyzes the codebase to generate statistics about the lines of code (LOC), comments, and file types. It processes source code files and generates a detailed report.

Usage:

```sh
python code_statistics.py <directory>
```

<directory>: The directory containing the code files to be analyzed.
Features:

Counts total lines of code, comments, and blank lines.
Generates a report with statistics for each file type.
Provides a summary of the codebase structure.
2. code_statistics_multiprocessing.py
   This script is an enhanced version of code_statistics.py that utilizes multiprocessing to speed up the analysis of large codebases.

Usage:

```sh
python code_statistics_multiprocessing.py <directory>
```

<directory>: The directory containing the code files to be analyzed.
Features:

Similar to code_statistics.py but with multiprocessing support for faster execution.
Efficiently processes large directories by parallelizing the analysis.
Generates a comprehensive report with detailed code statistics.
3. create_random_files.py
   This script creates a specified number of subdirectories and files within a given parent directory. It is useful for generating test data for file system operations.

Usage:

```sh
python create_random_files.py <parent_directory> <num_subdirs> <num_files> <max_depth>
```

<parent_directory>: The parent directory where subdirectories and files will be created.
<num_subdirs>: The number of subdirectories to create.
<num_files>: The number of files to create in each subdirectory.
<max_depth>: The maximum depth of the subdirectory structure.
Features:

Creates a random file and directory structure for testing purposes.
Generates files with random content.
Provides a summary of the generated file system structure and statistics.
You can now refer to this updated README.md for instructions on how to use each script and their respective features.






