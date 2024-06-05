import os
import tarfile
import zipfile
import tempfile
import shutil
from collections import defaultdict

# Function to extract archives using tar, gz, or zip format
def extract(archive, extract_to):
    try:
        if archive.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tgz')):
            with tarfile.open(archive, 'r:*') as tar:
                tar.extractall(path=extract_to)
        elif archive.endswith('.zip'):
            with zipfile.ZipFile(archive, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        else:
            print(f"Error: Unknown archive format for file '{archive}'", file=sys.stderr)
            exit(1)
    except Exception as e:
        print(f"Error: Failed to extract archive '{archive}': {e}", file=sys.stderr)
        exit(1)

# Function to determine the language of a file based on its extension
def get_lang(file):
    return file.split('.')[-1].lower()

# Comment symbols for each file extension
comment_symbols = {
    '.py': ('#', ('"""', '"""')),
    '.cjs': ('//', ('/*', '*/')),
    '.js': ('//', ('/*', '*/')),
    '.mjs': ('//', ('/*', '*/')),
    '.ts': ('//', ('/*', '*/')),
    '.tsx': ('//', ('/*', '*/')),
    '.c': ('//', ('/*', '*/')),
    '.h': ('//', ('/*', '*/')),
    '.cpp': ('//', ('/*', '*/')),
    '.cc': ('//', ('/*', '*/')),
    '.cxx': ('//', ('/*', '*/')),
    '.hpp': ('//', ('/*', '*/')),
    '.hxx': ('//', ('/*', '*/')),
    '.h++': ('//', ('/*', '*/')),
    '.inl': ('//', ('/*', '*/')),
    '.ipp': ('//', ('/*', '*/')),
    '.tcc': ('//', ('/*', '*/')),
    '.tpp': ('//', ('/*', '*/')),
    '.java': ('//', ('/*', '*/')),
    '.r': ('#', ('/*', '*/')),
    '.rdata': ('#', ('/*', '*/')),
    '.rds': ('#', ('/*', '*/'))
}

# Function to count lines of code and update statistics for each language
def count_loc(file, lang_stats):
    global tot_loc
    extension = os.path.splitext(file)[1].lower()
    if extension == '.py':
        print("test")
    single_line_comment_symbol, multi_line_comment_symbols = comment_symbols.get(extension, ('#', ('"""', '"""')))
    
    loc = 0
    comment_loc = 0
    in_multi_line_comment = False

    with open(file, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line:
                loc += 1
                if in_multi_line_comment:
                    comment_loc += 1
                    if multi_line_comment_symbols[1] in line:
                        in_multi_line_comment = False
                elif line.startswith(multi_line_comment_symbols[0]):
                    comment_loc += 1
                    in_multi_line_comment = True
                elif line.startswith(multi_line_comment_symbols[0]):
                    comment_loc += 1
                elif line.startswith(single_line_comment_symbol):
                    comment_loc += 1

    tot_loc += loc
    lang_stats[extension]['total'] += loc
    lang_stats[extension]['comments'] += comment_loc
    lang_stats[extension]['code'] += (loc - comment_loc)
    print(f"Counted {loc} lines in {file} (extension: {extension}, {loc - comment_loc} code - {comment_loc} comments)")

# Function to find archives in the search directory
def find_archives(search_dir):
    archives = []
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.endswith(('.tar.gz', '.tar.bz2', '.tar', '.zip', '.tgz')):
                archives.append(os.path.join(root, file))
    return archives

# Function to recursively extract all archives
def extract_all_archives(search_dir):
    archive_types = defaultdict(int)
    
    while True:
        archives = find_archives(search_dir)
        if not archives:
            break

        for archive in archives:
            print(f"Found archive: {archive}")
            archive_type = os.path.splitext(archive)[-1].lower()
            archive_types[archive_type] += 1

            temp_dir = tempfile.mkdtemp()
            try:
                extract(archive, temp_dir)
                for item in os.listdir(temp_dir):
                    s = os.path.join(temp_dir, item)
                    d = os.path.join(search_dir, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.move(s, d)
                    else:
                        shutil.move(s, d)
            finally:
                shutil.rmtree(temp_dir)
            
            os.remove(archive)
    
    return archive_types

# Function to process source code files in a single extracted directory
def process_files_in_directory(directory):
    global lang_stats, total_files_found, file_type_counts
    print(f"Processing directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tar.gz', '.tar.bz2', '.tar', '.zip', '.tgz')):
                continue  # Skip archive files
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            try:
                count_loc(file_path, lang_stats)
                file_type_counts[os.path.splitext(file)[1].lower()] += 1
                total_files_found += 1
            except Exception as e:
                print(f"Error processing file {file_path}: {e}", file=sys.stderr)

# Initialize variables for the total lines of code and the language statistics
tot_loc = 0
total_files_found = 0
lang_stats = defaultdict(lambda: {'total': 0, 'code': 0, 'comments': 0})
file_type_counts = defaultdict(int)

# Function to generate the codebase report
def create_report(report_path, archive_types):
    with open(report_path, 'w') as report_file:
        report_file.write(f"Total archives found: {sum(archive_types.values())}\n")
        report_file.write("Archives by type:\n")
        for ext, count in archive_types.items():
            report_file.write(f"{ext}: {count}\n")
        
        report_file.write(f"\nTotal files found: {total_files_found}\n")
        report_file.write(f"Total lines of code found: {tot_loc}\n\n")
        
        report_file.write("Files of each type found:\n")
        for ext in sorted(file_type_counts):
            report_file.write(f"{ext}: {file_type_counts[ext]}\n")
        
        report_file.write("\nLanguage statistics:\n")
        for lang in sorted(lang_stats):
            count = lang_stats[lang]['total']
            code_count = lang_stats[lang]['code']
            comment_count = lang_stats[lang]['comments']
            percentage = (count / tot_loc) * 100 if tot_loc > 0 else 0
            report_file.write(f"{lang}: {count} lines [{code_count} code - {comment_count} comments] ({percentage:.2f}%)\n")

# Main script execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python script.py <search_directory>")
        sys.exit(1)

    search_dir = sys.argv[1]
    
    try:
        archive_types = extract_all_archives(search_dir)
        process_files_in_directory(search_dir)
        create_report(os.path.join(search_dir, "codebase_report.txt"), archive_types)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
