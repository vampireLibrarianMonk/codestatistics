import os
import tarfile
import zipfile
import tempfile
import shutil
from collections import defaultdict
from multiprocessing import Pool, Manager, cpu_count
import argparse
import sys

# Function to extract archives using tar, gz, or zip format
def extract(archive, extract_to, archive_types, lock):
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

        archive_type = os.path.splitext(archive)[-1].lower()
        with lock:
            archive_types[archive_type] = archive_types.get(archive_type, 0) + 1
    except Exception as e:
        print(f"Error: Failed to extract archive '{archive}': {e}", file=sys.stderr)
        exit(1)

# Function to determine the language of a file based on its extension or return the file name if no extension exists
def get_lang(file):
    # Check if the file has an extension
    extension = os.path.splitext(file)[1].lower()
    if extension:
        return extension
    else:
        return os.path.basename(file).lower()

# Function to count lines of code and update statistics for each language
def count_loc(loc, file, lang_stats, tot_loc, file_type_counts, lock):
    with lock:
        tot_loc.value += loc
        lang = get_lang(file)
        lang_stats[lang] = lang_stats.get(lang, 0) + loc
        file_type_counts[lang] = file_type_counts.get(lang, 0) + 1

# Function to find archives in the search directory
def find_archives(search_dir):
    archives = []
    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.endswith(('.tar.gz', '.tar.bz2', '.tar', '.zip', '.tgz')):
                archives.append(os.path.join(root, file))
    return archives

# Function to recursively extract all archives
def extract_all_archives(search_dir, archive_types, lock):
    while True:
        archives = find_archives(search_dir)
        if not archives:
            break

        for archive in archives:
            print(f"Found archive: {archive}")
            temp_dir = tempfile.mkdtemp()
            try:
                extract(archive, temp_dir, archive_types, lock)
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

# Function to process source code files in a single extracted directory
def process_files_in_directory(directory, lang_stats, tot_loc, file_type_counts, total_files_found, lock):
    print(f"Processing directory: {directory} with PID: {os.getpid()}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.tar.gz', '.tar.bz2', '.tar', '.zip', '.tgz')):
                continue  # Skip archive files
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path} with PID: {os.getpid()}")
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    loc = sum(1 for _ in f)
                count_loc(loc, file_path, lang_stats, tot_loc, file_type_counts, lock)
                with lock:
                    total_files_found.value += 1
            except Exception as e:
                print(f"Error processing file {file_path}: {e}", file=sys.stderr)

# Function to generate the codebase report
def create_report(report_path, archive_types, total_files_found, tot_loc, file_type_counts, lang_stats):
    with open(report_path, 'w') as report_file:
        report_file.write(f"Total archives found: {sum(archive_types.values())}\n")
        report_file.write("Archives by type:\n")
        for ext, count in archive_types.items():
            report_file.write(f"{ext}: {count}\n")

        report_file.write(f"\nTotal files found: {total_files_found.value}\n")
        report_file.write(f"Total lines of code found: {tot_loc.value}\n\n")

        report_file.write("Files of each type found:\n")
        for ext in sorted(file_type_counts.keys()):
            report_file.write(f"{ext}: {file_type_counts[ext]}\n")

        report_file.write("\nLanguage statistics:\n")
        for lang in sorted(lang_stats.keys()):
            count = lang_stats[lang]
            percentage = (count / tot_loc.value) * 100 if tot_loc.value > 0 else 0
            report_file.write(f"{lang}: {count} lines ({percentage:.2f}%)\n")

# Main script execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze codebase and generate statistics")
    parser.add_argument("search_directory", help="Directory to search for code files and archives")
    parser.add_argument("--cpus", type=int, default=cpu_count() - 1, help="Number of CPUs to use (default: one less than the total number of CPUs)")

    args = parser.parse_args()

    search_dir = args.search_directory
    num_cpus = args.cpus

    try:
        manager = Manager()
        lang_stats = manager.dict()
        tot_loc = manager.Value('i', 0)
        file_type_counts = manager.dict()
        total_files_found = manager.Value('i', 0)
        archive_types = manager.dict()
        lock = manager.Lock()

        extract_all_archives(search_dir, archive_types, lock)

        subdirs = [os.path.join(search_dir, d) for d in os.listdir(search_dir) if os.path.isdir(os.path.join(search_dir, d))]

        with Pool(processes=num_cpus) as pool:
            pool.starmap(process_files_in_directory, [(subdir, lang_stats, tot_loc, file_type_counts, total_files_found, lock) for subdir in subdirs])

        create_report(os.path.join(search_dir, "codebase_report.txt"), archive_types, total_files_found, tot_loc, file_type_counts, lang_stats)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)