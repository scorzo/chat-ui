import shelve

def store_file(file_name, file_id):
    """Store a file by name without overwriting existing entries.
    Returns file_id on success, None otherwise."""
    with shelve.open("files_db", writeback=True) as files_shelf:
        if file_name in files_shelf:
            print(f"Duplicate name warning: '{file_name}' already exists.")
            return None
        else:
            files_shelf[file_name] = file_id
            return file_id

def check_if_file_exists(file_name):
    """Checks if a file exists by name and returns the file_id if it exists, None otherwise."""
    with shelve.open("files_db") as files_shelf:
        return files_shelf.get(file_name, None)

def print_all_files():
    """Prints all file names and their corresponding file_ids."""
    with shelve.open("files_db") as files_shelf:
        for file_name, file_id in files_shelf.items():
            print(f"File Name: {file_name} has File ID: {file_id}")

if __name__ == '__main__':
    # This code block will only execute if the script is run directly
    print("Printing all files:")
    print_all_files()
