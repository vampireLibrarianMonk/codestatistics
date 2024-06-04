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
    "python": [".py", ".pyc", ".pyd", ".pyo", ".pyw"],
    "r": [".r", ".rdata", ".rds"],
    "java": [".java"],
    "cpp": [".cc", ".cpp", ".cxx", ".h", ".hpp", ".hxx", ".h++", ".inl", ".ipp", ".tcc", ".tpp"]
}

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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

def create_random_code_lines(num_lines):
    code_lines = []
    for _ in range(num_lines):
        line_length = random.randint(10, 80)  # Random length of each code line
        code_lines.append(random_string(line_length))
    return '\n'.join(code_lines)

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

def create_files_in_directory(parent_directory, num_subdirs, num_files, max_depth):
    os.makedirs(parent_directory, exist_ok=True)
    
    total_files_created = 0
    subdirs_created = set()
    file_type_counts = defaultdict(int)
    lang_stats = defaultdict(int)
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
                num_lines = random.randint(5, 20)  # Random number of lines of code
                with open(file_path, 'w') as file:
                    file.write(create_random_code_lines(num_lines))
                
                file_type_counts[extension] += 1
                lang_stats[extension] += num_lines
                tot_loc += num_lines
                total_files_created += 1

    # Archive the subdirectories starting from the deepest one
    sorted_subdirs = sorted(subdirs_created, key=lambda x: x.count(os.sep), reverse=True)
    for subdir_path in sorted_subdirs:
        archive_format = random.choice(['zip', 'tar', 'gztar', 'bztar'])
        archive_directory(subdir_path, archive_format)

    return len(subdirs_created), total_files_created, file_type_counts, lang_stats, tot_loc

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
        
        report_file.write("\nCode statistics:\n")
        for ext in sorted(lang_stats):
            count = lang_stats[ext]
            percentage = (count / tot_loc) * 100 if tot_loc > 0 else 0
            report_file.write(f"{ext}: {count} lines ({percentage:.2f}%)\n")

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
