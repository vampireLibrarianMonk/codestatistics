import os
import random
import string
import sys
import shutil
from collections import defaultdict

# Mapping of programming languages to their possible file extensions
file_extensions = {
    "javascript": [".cjs", ".js", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "c": [".c", ".h"],
    "python": [".py"],
    "r": [".r", ".rdata", ".rds"],
    "java": [".java"],
    "cpp": [".cc", ".cpp", ".cxx", ".h", ".hpp", ".hxx", ".h++", ".inl", ".ipp", ".tcc", ".tpp"],
    "": [""],
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

# Function to generate a random string
def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to create a random subdirectory path with a given maximum depth
def create_random_subdirectory_path(base_path, max_depth):
    depth = random.randint(1, max_depth)
    subdir_path = base_path
    subdir_paths = []
    for _ in range(depth):
        subdir_name = str(random.randint(1000, 9999))
        subdir_path = os.path.join(subdir_path, subdir_name)
        subdir_paths.append(subdir_path)
        os.makedirs(subdir_path, exist_ok=True)
    return subdir_paths

# Function to create random code lines with comments
def create_random_code_lines(extension):
    num_lines = random.randint(5, 20)  # Random number of lines of code
    code_lines = []

    if not extension:
        print()

    single_line_comment_symbol, multi_line_comment_symbols = comment_symbols.get(extension, ('#', ('"""', '"""')))
    comment_count = 0
    code_count = 0

    for _ in range(num_lines):
        if random.random() < 0.1 and extension:  # 10% chance to start a multi-line comment
            code_lines.append(multi_line_comment_symbols[0])
            filler_lines = random.randint(1, 5)
            for _ in range(filler_lines):
                code_lines.append(random_string(random.randint(10, 80)))
                comment_count += 1
            code_lines.append(multi_line_comment_symbols[1])
            comment_count += 2  # Start and end symbols
        elif random.random() < 0.2 and extension:  # 20% chance to add a single-line comment
            line_length = random.randint(10, 80)
            code_lines.append(single_line_comment_symbol + ' ' + random_string(line_length))
            comment_count += 1
        else:
            line_length = random.randint(10, 80)
            code_lines.append(random_string(line_length))
            code_count += 1

    total_lines = comment_count + code_count
    return '\n'.join(code_lines), code_count, comment_count, total_lines

# Function to archive a directory in a specified format
def archive_directory(directory, archive_format):
    base_name = directory
    root_dir = os.path.dirname(directory)
    if archive_format == 'zip':
        shutil.make_archive(base_name, 'zip', root_dir, os.path.basename(directory))
    elif archive_format == 'tar':
        shutil.make_archive(base_name, 'tar', root_dir, os.path.basename(directory))
    elif archive_format == 'gztar':
        shutil.make_archive(base_name, 'gztar', root_dir, os.path.basename(directory))
    elif archive_format == 'bztar':
        shutil.make_archive(base_name, 'bztar', root_dir, os.path.basename(directory))
    # Clean up the directory after archiving
    shutil.rmtree(directory)

# Function to create files in a directory with specified parameters
def create_files_in_directory(parent_directory, num_subdirs, num_files, max_depth):
    os.makedirs(parent_directory, exist_ok=True)

    total_files_created = 0
    subdirs_created = set()
    file_type_counts = defaultdict(int)
    lang_stats = defaultdict(lambda: {'total': 0, 'code': 0, 'comments': 0})
    tot_loc = 0

    for _ in range(num_subdirs):
        subdir_paths = create_random_subdirectory_path(parent_directory, max_depth)
        subdirs_created.update(subdir_paths)

        for subdir_path in subdir_paths:
            for _ in range(num_files):
                # Choose a random language and extension
                language = random.choice(list(file_extensions.keys()))
                extension = random.choice(file_extensions[language]).lower()  # Ensure extension is in lowercase

                # Create a random filename
                file_name = random_string(random.randint(5, 10)) + extension
                file_path = os.path.join(subdir_path, file_name)

                # Write random code lines to the file
                code, code_count, comment_count, total_lines = create_random_code_lines(extension)
                with open(file_path, 'w') as file:
                    file.write(code)

                file_type_counts[extension] += 1
                lang_stats[extension]['total'] += total_lines
                lang_stats[extension]['comments'] += comment_count
                lang_stats[extension]['code'] += code_count
                tot_loc += total_lines
                total_files_created += 1

                # Debugging output to verify line counts
                print(f"Generated {total_lines} lines in {file_name} ({code_count} code - {comment_count} comments)")

    # Archive the subdirectories starting from the deepest one
    sorted_subdirs = sorted(subdirs_created, key=lambda x: x.count(os.sep), reverse=True)
    for subdir_path in sorted_subdirs:
        archive_format = random.choice(['zip', 'tar', 'gztar', 'bztar'])
        archive_directory(subdir_path, archive_format)

    return len(subdirs_created), total_files_created, file_type_counts, lang_stats, tot_loc

# Function to write statistics to a file
def write_statistics_to_file(statistics, output_file_path, parent_directory, num_subdirs, num_files, max_depth):
    subdirs_created, total_files_created, file_type_counts, lang_stats, tot_loc = statistics

    with open(output_file_path, 'w') as report_file:
        report_file.write(f"Parent directory: {parent_directory}\n")
        report_file.write(f"Number of subdirectories: {num_subdirs}\n")
        report_file.write(f"Number of files per subdirectory: {num_files}\n")
        report_file.write(f"Maximum subdirectory depth: {max_depth}\n\n")

        report_file.write(f"Total subdirectories created: {subdirs_created}\n")
        report_file.write(f"Total files created: {total_files_created}\n")
        report_file.write(f"Total lines of code generated: {tot_loc}\n\n")

        report_file.write("Files of each type created:\n")
        for ext in sorted(file_type_counts):
            report_file.write(f"{ext}: {file_type_counts[ext]}\n")

        report_file.write("\nLanguage statistics:\n")
        for ext in sorted(lang_stats):
            count = lang_stats[ext]['total']
            code_count = lang_stats[ext]['code']
            comment_count = lang_stats[ext]['comments']
            percentage = (count / tot_loc) * 100 if tot_loc > 0 else 0
            report_file.write(f"{ext}: {count} lines [{code_count} code - {comment_count} comments] ({percentage:.2f}%)\n")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <parent_directory> <num_subdirs> <num_files> <max_depth>")
        sys.exit(1)

    parent_directory = sys.argv[1]
    num_subdirs = int(sys.argv[2])
    num_files = int(sys.argv[3])
    max_depth = int(sys.argv[4])

    statistics = create_files_in_directory(parent_directory, num_subdirs, num_files, max_depth)
    output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generation_statistics.txt")
    write_statistics_to_file(statistics, output_file_path, parent_directory, num_subdirs, num_files, max_depth)

    print(f"Created {statistics[0]} subdirectories with random depths and {statistics[1]} files each in {parent_directory}")
    print(f"Statistics written to {output_file_path}")