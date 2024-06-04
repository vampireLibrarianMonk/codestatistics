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

# Function to count lines of code and update statistics for each language
def count_loc(loc, file, lang_stats):
    global tot_loc
    tot_loc += loc
    lang = get_lang(file)
    lang_stats[lang] += loc
    print(f"Counted {loc} lines in {file} (language: {lang})")

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
                with open(file_path, 'r', errors='ignore') as f:
                    loc = sum(1 for _ in f)
                count_loc(loc, file_path, lang_stats)
                file_type_counts[get_lang(file)] += 1
                total_files_found += 1
            except Exception as e:
                print(f"Error processing file {file_path}: {e}", file=sys.stderr)

# Initialize variables for the total lines of code and the language statistics
tot_loc = 0
total_files_found = 0
lang_stats = defaultdict(int)
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
            count = lang_stats[lang]
            percentage = (count / tot_loc) * 100 if tot_loc > 0 else 0
            report_file.write(f"{lang}: {count} lines ({percentage:.2f}%)\n")

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
