import os
import zipfile
import tarfile
import sys
import shutil

# Terms to search for
LICENSE_TERMS = [
    "License", "Copyright", "All rights reserved",
    "Proprietary", "Confidential", "Terms of use",
    "Redistribution", "Warranty"
]

# Report file path
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proprietary_terms_statistics.txt")

# Supported archive formats
SUPPORTED_ARCHIVE_FORMATS = ['.tar', '.tar.gz', '.tar.bz2', '.tgz', '.zip']

def search_in_content(content, file_path, archive_path):
    found_terms = []
    lower_content = content.lower()
    for term in LICENSE_TERMS:
        if term.lower() in lower_content:
            found_terms.append((term, file_path, archive_path))
    return found_terms

def search_in_file(file_path, relative_path, archive_path):
    found_terms = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            found_terms = search_in_content(content, relative_path, archive_path)
    except UnicodeDecodeError:
        print(f"Skipping binary file: {file_path}")
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
    return found_terms

def extract_archive(archive_path, extract_to):
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_to)
    elif archive_path.endswith(tuple(SUPPORTED_ARCHIVE_FORMATS)):
        mode = 'r:gz' if archive_path.endswith(('.tar.gz', '.tgz')) else 'r:bz2' if archive_path.endswith('.tar.bz2') else 'r'
        with tarfile.open(archive_path, mode) as tar:
            tar.extractall(extract_to)

def search_in_directory(directory, archive_root, archive_path):
    found_terms_all = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, archive_root)
            if file_path.endswith(tuple(SUPPORTED_ARCHIVE_FORMATS)):
                tmp_dir = os.path.join(root, 'tmp')
                os.makedirs(tmp_dir, exist_ok=True)
                extract_archive(file_path, tmp_dir)
                found_terms = search_in_directory(tmp_dir, archive_root, archive_path)
                found_terms_all.extend(found_terms)
                shutil.rmtree(tmp_dir)
            else:
                found_terms = search_in_file(file_path, relative_path, archive_path)
                found_terms_all.extend(found_terms)
    return found_terms_all

def search_in_designated_directory(archives_dir):
    found_terms_all = []
    for root, _, files in os.walk(archives_dir):
        for file in files:
            archive_path = os.path.join(root, file)
            if os.path.isfile(archive_path) and archive_path.endswith(tuple(SUPPORTED_ARCHIVE_FORMATS)):
                tmp_dir = os.path.join(root, 'tmp')
                os.makedirs(tmp_dir, exist_ok=True)
                extract_archive(archive_path, tmp_dir)
                found_terms = search_in_directory(tmp_dir, tmp_dir, archive_path)
                found_terms_all.extend(found_terms)
                shutil.rmtree(tmp_dir)
            elif os.path.isfile(archive_path):
                found_terms = search_in_file(archive_path, archive_path, root)
                found_terms_all.extend(found_terms)
            else:
                print(f"Skipping '{archive_path}' as it is not a supported archive format.")
    return found_terms_all

def write_report(found_terms):
    with open(LOG_FILE, 'w') as report_file:
        report_file.write("Proprietary Terms Statistics:\n\n")
        term_counts = {term: 0 for term in LICENSE_TERMS}
        for term, file_path, archive_path in found_terms:
            term_counts[term] += 1
            report_file.write(f"Term: {term}, File: {file_path}, Archive: {archive_path}\n")
        report_file.write("\nSummary:\n\n")
        for term, count in term_counts.items():
            report_file.write(f"{term}: {count}\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <base_search_directory>")
        sys.exit(1)

    base_search_directory = sys.argv[1]
    if not os.path.exists(base_search_directory):
        print(f"Error: {base_search_directory} does not exist.")
        sys.exit(1)

    found_terms = search_in_designated_directory(base_search_directory)
    write_report(found_terms)
    print("Report generated successfully.")
