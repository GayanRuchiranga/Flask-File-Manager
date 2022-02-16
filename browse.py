import json
import traceback
import os
import filetype
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

class FileBrowser:
    def __init__(self):
        # Config Data
        config = load_config()
        self.root_dir = config["root_dir"]
        self.hidden_list = config["hidden"]
        self.max_name_length = config["max_name_length"]

        self.current_dir = ""
        self.breadcrumbs = []
        self.errors = []
        self.directories_info = {}
        self.files_info = {}

    def is_hidden(self, path):
        for i in self.hidden_list:
            if i != '' and str(Path(i)) == str(Path(path)):
                return True
        return False

    def changeDirectory(self, path, prev_path):
        # os.system('cls')
        if not os.path.exists(build_path([self.root_dir, path])):
            self.errors.append(f"Invalid Directory Path")
            self.current_dir =  prev_path
        elif self.is_hidden(build_path([self.root_dir, path])):
            self.errors.append(f"Permission Denied")
            self.current_dir =  prev_path
        else:
            self.current_dir =  path
        self.build_breadcrumbs(path)
        self.getDirList()


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
                    "is_active":True if breadcrumb == path_parts[-1] else False,
                    "path_link":f"/browser/{'/'.join(path_parts[:index+1])}"
                })


    def getDirList(self):
        tp_dict = {
            'image': 'photo-icon.png', 
            'audio': 'audio-icon.png',
            'video': 'video-icon.png',
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
            "json":"json_icon.png"
            }

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
                image = None
                try:
                    kind = filetype.guess(file)
                    print(kind)
                    if kind:
                        tp = kind.mime.split('/')[0]
                        if tp in tp_dict:
                            image = tp_dict[tp]
                except:
                    pass

                if not image:
                    image = 'default_file.png'

                if file.split(".")[1].lower() in tp_dict:
                    image = tp_dict[file.split(".")[1].lower()]

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
        