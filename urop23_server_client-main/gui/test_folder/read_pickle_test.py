import pickle
import os

folder = "C:\\Users\\Berkin\\Desktop\\MIT\\Junior\\UROP\\Summer\\urop23_server_client\\gui\\test_folder\\sweep_test"

# Get all file names in the folder
file_names = os.listdir(folder)

# Loop through the file names
file_name = '65_0_2023-07-21-14_49_40.pkl'
# Check if the file is a pickle file
if file_name.endswith(".pkl"):
    # Load pickle file
    file_path = os.path.join(folder, file_name)
    try:
        with open(file_path, "rb") as file:
            loaded_data_dict = pickle.load(file)
        print(loaded_data_dict)
    except EOFError:
        print(f"Error: Unable to load data from {file_path}. The file may be empty or corrupted.")
