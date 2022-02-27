import json
import shutil
import traceback
import os
from pathlib import Path
from datetime import datetime
from hurry.filesize import size
from natsort import natsorted

def load_config():
    try:
        with open('config.json') as json_data_file:
            return json.load(json_data_file)
    except Exception as ex:
        print(traceback.format_exc())

def build_path(parts):
    parts = [part for part in parts if part]
    return str(Path("/".join(parts)))

def get_file_image(file):
    file_image_dict = {
        "pdf":"pdf_icon.png", 
        "py":"python_icon.png", 
        "zip":"zip_icon.png", 
        "rar":"rar_icon.png", 
        "pyt":"nn_model.png", 
        "net":"nn_model.png", 
        "xml":"xml_icon.jpg",
        "csv":"csv_icon.png",
        "xls":"excel_icon.jpg",
        "xlsx":"excel_icon.jpg",
        "doc":"word_icon.png",
        "docx":"word_icon.png",
        "json":"json_icon.png",
        "html":"html_icon.png",
        "css":"css_icon.png",
        "js":"javascript_icon.png"
    }
    mime_type = Path(file).suffix.lower().replace(".","")
    image = 'default_file.png'
    if mime_type in file_image_dict:
        image = file_image_dict[mime_type]
    return image

class FileBrowser:
    def __init__(self):
        # Config Data
        config = load_config()
        self.root_dir = config["root_dir"]
        if not self.root_dir.strip() or not os.path.exists(self.root_dir) or not os.path.isdir(self.root_dir):
            self.root_dir = os.getcwd()
        self.hidden_list = config["hidden"]
        self.max_name_length = config["max_name_length"]

        self.current_dir = ""
        self.breadcrumbs = []
        self.messages = []
        self.directories_info = {}
        self.files_info = {}

    def is_hidden(self, path):
        for hidden_path in self.hidden_list:
            if hidden_path.strip() != '' and build_path([self.root_dir, hidden_path]) in path:
                return True
        return False

    def change_directory(self, path, prev_path):
        # os.system('cls')
        if not os.path.exists(build_path([self.root_dir, path])):
            self.messages.append({"type":"error","message":"Invalid Directory Path"})
            self.current_dir =  prev_path
        elif self.is_hidden(build_path([self.root_dir, path])):
            self.messages.append({"type":"error","message":"Hidden Directory, Permission Denied"})
            self.current_dir =  prev_path
        else:
            self.current_dir =  path
        try:
            self.get_dir_list()
        except PermissionError:
            self.messages.append({"type":"error","message":"Permission Denied"})
            self.current_dir =  prev_path
        self.get_dir_list()
        self.build_breadcrumbs(self.current_dir)


    def build_breadcrumbs(self, path):
        self.breadcrumbs.append(
            {
                "breadcrumb":"Home",
                "is_active": True if not path.strip() else False,
                "path_link":"/browser/"
            })
        path_parts = Path(path).parts
        for index, breadcrumb in enumerate(path_parts):
            self.breadcrumbs.append(
                {
                    "breadcrumb":breadcrumb,
                    "is_active":True if '/'.join(path_parts[:index+1]) == path else False,
                    "path_link":f"/browser/{'/'.join(path_parts[:index+1])}"
                })

    def create_new_directory(self, directory_path):
        try:
            os.mkdir(build_path([self.root_dir, directory_path]))
            self.messages.append({"type":"success","message":"Folder Created"})
        except FileExistsError:
            self.messages.append({"type":"error","message":"Folder Exists"})
        except OSError:
            self.messages.append({"type":"error","message":"Invalid Folder Name"})

    def get_dir_list(self):
        directories = natsorted([dir for dir in os.listdir(build_path([self.root_dir, self.current_dir])) if os.path.isdir(build_path([self.root_dir, self.current_dir, dir]))])
        files = natsorted([file for file in os.listdir(build_path([self.root_dir, self.current_dir])) if os.path.isfile(build_path([self.root_dir, self.current_dir, file]))])

        for dir in directories:
            if not self.is_hidden(build_path([self.root_dir, self.current_dir, dir])):
                image = 'folder_icon2.png'

                if len(dir) > self.max_name_length:
                    dots = "..."
                else:
                    dots = ""

                dir_stats = os.stat(build_path([self.root_dir, self.current_dir, dir]))
                self.directories_info[dir] = {}
                self.directories_info[dir]['name'] = dir[0:self.max_name_length] + dots
                self.directories_info[dir]['relative_path'] = build_path([self.current_dir, dir])
                self.directories_info[dir]['full_name'] = dir
                self.directories_info[dir]['image'] = image
                self.directories_info[dir]['date_created'] = datetime.utcfromtimestamp(dir_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                self.directories_info[dir]['date_modified'] = datetime.utcfromtimestamp(dir_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                self.directories_info[dir]['size'] = "---"

        for file in files:
            if not self.is_hidden(build_path([self.root_dir, self.current_dir, file])):
                image = get_file_image(file)
                if len(file) > self.max_name_length:
                    dots = "..."
                else:
                    dots = ""

                self.files_info[file] = {}
                self.files_info[file]['name'] = file[0:self.max_name_length] + dots
                self.files_info[file]['relative_path'] = build_path([self.current_dir, file])
                self.files_info[file]['full_name'] = file
                self.files_info[file]['image'] = image

                try:
                    file_stats = os.stat(build_path([self.root_dir, self.current_dir, file]))
                    self.files_info[file]['date_created'] = datetime.utcfromtimestamp(file_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                    self.files_info[file]['date_modified'] = datetime.utcfromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    self.files_info[file]['size'] = size(file_stats.st_size)
                except:
                    self.files_info[file]['date_created'] = "---"
                    self.files_info[file]['date_modified'] = "---"
                    self.files_info[file]['size'] = "---"

    def perform_copy_cut(self, src, dst):
        full_source_path = build_path([self.root_dir, src['path']])
        full_destination_path = build_path([self.root_dir, dst])

        if not os.path.exists(full_source_path):
            self.messages.append({"type":"error","message":"Invalid source path"})
            return
        
        if not os.path.exists(full_destination_path):
            self.messages.append({"type":"error","message":"Invalid destination path"})
            return

        destination = ""
        if os.path.isdir(full_destination_path):
            destination = full_destination_path
        elif os.path.isfile(full_destination_path):
            destination = Path(full_destination_path).parent
        else:
            self.messages.append({"type":"error","message":"Invalid destination path"})
            return

        if str(Path(full_source_path)) == str(Path(os.path.join(destination, Path(full_source_path).name))):
            self.messages.append({"type":"error","message":"Unable to perform copy or cut into same directory"})
            return

        source_type = ""
        if os.path.isdir(full_source_path):
            source_type = "Folder"
            if src["action"] == "copy":
                shutil.copytree(full_source_path, os.path.join(destination, Path(full_source_path).name))
                self.messages.append({"type":"success","message":"Folder copied"})
        elif os.path.isfile(full_source_path):
            source_type = "File"
            if src["action"] == "copy":
                shutil.copyfile(full_source_path, os.path.join(destination, Path(full_source_path).name))
                self.messages.append({"type":"success","message":"File copied"})

        if src["action"] == "cut":
            shutil.move(full_source_path, os.path.join(destination, Path(full_source_path).name))
            self.messages.append({"type":"success","message":f"{source_type} moved"})
        elif src["action"] != "copy":
            self.messages.append({"type":"error","message":"Invalid action"})
            return
        