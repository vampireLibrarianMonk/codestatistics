import os
import random
import shutil
import tarfile
import zipfile
from pathlib import Path

# Mapping of programming languages to their possible file extensions
file_extensions = {
    "javascript": [".cjs", ".js", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "c": [".c", ".h"],
    "python": [".py"],
    "r": [".r", ".rdata", ".rds"],
    "java": [".java"],
    "cpp": [".cc", ".cpp", ".cxx", ".h", ".hpp", ".hxx", ".h++", ".inl", ".ipp", ".tcc", ".tpp"]
}

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
    '.h++': ('//', ('/*', '*/'))
}

LICENSE_TERMS = [
    "License", "Copyright", "All rights reserved",
    "Proprietary", "Confidential", "Terms of use",
    "Redistribution", "Warranty"
]

FILE_NAMES = [
    "LICENSE", "LICENSE.txt", "COPYING", "README.md",
    "NOTICE", "DISCLAIMER"
]

# File to log proprietary term locations
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proprietary_terms_report.txt")

def insert_terms(content, terms):
    term = random.choice(terms)
    position = random.randint(0, len(content))
    content = content[:position] + "\n" + term + "\n" + content[position:]
    return content, position, term


def generate_file_content():
    content = ""
    content, position, term = insert_terms(content, LICENSE_TERMS)
    return content, position, term


def create_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def extract_archive(archive_path, extract_to):
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_to)
    else:
        with tarfile.open(archive_path, 'r:*') as tar:
            tar.extractall(extract_to)


def create_archive(archive_path, source_dir):
    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'w') as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, source_dir))
    else:
        mode = 'w:gz' if archive_path.endswith(('.tar.gz', '.tgz')) else 'w:bz2' if archive_path.endswith(
            '.tar.bz2') else 'w'
        with tarfile.open(archive_path, mode) as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))


def add_files_to_archive(archive_path, generated_files, temp_dir):
    extract_dir = os.path.join(temp_dir, 'extracted')
    Path(extract_dir).mkdir(parents=True, exist_ok=True)

    extract_archive(archive_path, extract_dir)

    for file_path, content, position, term in generated_files:
        dest_path = os.path.join(extract_dir, os.path.relpath(file_path, temp_dir))
        create_file(dest_path, content)

        # Log the location of inserted proprietary term
        with open(LOG_FILE, 'a') as log:
            log.write(f"File: {archive_path}, Position: {position}, Term: {term}\n")

    os.remove(archive_path)
    create_archive(archive_path, extract_dir)
    shutil.rmtree(extract_dir)


def generate_files(directory, max_files=None):
    Path(directory).mkdir(parents=True, exist_ok=True)
    generated_files = []

    num_files = 0

    for name in FILE_NAMES:
        if max_files is not None and num_files >= max_files:
            break
        file_path = os.path.join(directory, name)
        content, position, term = generate_file_content()
        create_file(file_path, content)
        generated_files.append((file_path, content, position, term))
        num_files += 1

    for ext in [ext for exts in file_extensions.values() for ext in exts]:
        if max_files is not None and num_files >= max_files:
            break
        file_path = os.path.join(directory, f"file{ext}")
        content, position, term = generate_file_content()
        create_file(file_path, content)
        generated_files.append((file_path, content, position, term))
        num_files += 1

    return generated_files[:max_files] if max_files is not None else generated_files


def process_archives(parent_directory, temp_dir, max_files=None):
    for root, _, files in os.walk(parent_directory):
        for file in files:
            archive_path = os.path.join(root, file)
            if any(archive_path.endswith(ext) for ext in ['.zip', '.tar.gz', '.tgz', '.tar.bz2', '.tar']):
                generated_files = generate_files(temp_dir, max_files)
                add_files_to_archive(archive_path, generated_files, temp_dir)
                print(f"Updated archive: {archive_path}")
                shutil.rmtree(temp_dir)
                Path(temp_dir).mkdir(parents=True, exist_ok=True)


def main(parent_directory, max_files=None):
    temp_dir = 'temp_generated_files'
    process_archives(parent_directory, temp_dir, max_files)
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python insert_proprietary_terms.py <parent_directory> [max_files_per_subdirectory]")
    else:
        parent_directory = sys.argv[1]
        max_files = int(sys.argv[2]) if len(sys.argv) == 3 else 10
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)  # Clear the previous log file
        main(parent_directory, max_files)
