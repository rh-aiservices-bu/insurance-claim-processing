#%%
import re
import os

def extract_file_names(content):
    pattern = r'xref:(.*?)[\[\*]'
    matches = re.findall(pattern, content)
    # print(matches)
    return matches
#%%


def create_files(file_names):
    for name in file_names:
        name = "pages/"+name
        file_path = f"{name}"
        print(file_path)
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write(f"= {name}\n\n")
        else:
            print(f"File '{file_path}' already exists. Skipping.")


#%%

def main():
    with open("nav.adoc", "r") as nav_file:
        content = nav_file.read()

    file_names = extract_file_names(content)

    create_files(file_names)
#%%

if __name__ == "__main__":
    main()
# %%
