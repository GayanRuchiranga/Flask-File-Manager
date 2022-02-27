import tempfile
from flask import Blueprint, render_template, request, send_file, redirect, session, jsonify, flash
from flask_login import login_required, current_user
from browse import FileBrowser, build_path
import os
from io import BytesIO
import zipfile
from pathlib import Path

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return render_template('login.html')

@main.route('/changeView')
def changeView():
    default_view = int(session.get("default_view", 0))
    v = int(request.args.get('view', 0))
    if v in [0, 1]:
        default_view = v
    else:
        default_view = 0
    session["default_view"] = default_view
    return jsonify({
        "txt": default_view,
    })

@main.route('/browser/', methods=['GET'])
@main.route('/browser/<path:relative_path>', methods=['GET'])
@login_required
def browser(relative_path=""):
    file_browser = FileBrowser()
    file_browser.messages.extend(session.get('messages',[]))
    file_browser.change_directory(relative_path, session.get("prev_path",""))
    session.pop('messages', None)
    session["prev_path"] = file_browser.current_dir

    return render_template('browser.html',
    messages = file_browser.messages,
    breadcrumbs = file_browser.breadcrumbs,
    dirs_info = file_browser.directories_info,
    files_info = file_browser.files_info,
    default_view = int(session.get("default_view", 0)),
    copy_cut = session.get('copy_cut',{}),
    current_directory = file_browser.current_dir)


@main.route('/download_file/<path:file>')
@login_required
def download_file(file):
    file_browser = FileBrowser()
    full_path = build_path([file_browser.root_dir, file])
    if not os.path.exists(full_path):
        return render_template('404.html', errorText='Invalid File')
    
    if not os.path.isfile(full_path):
        return render_template('404.html', errorText='Not a File')

    if file_browser.is_hidden(full_path):
        return render_template('404.html', errorText='File Hidden')

    return send_file(full_path, attachment_filename=file.split("/")[-1])


@main.route('/download_folder/<path:directory>')
@login_required
def download_directory(directory):
    file_browser = FileBrowser()
    full_path = build_path([file_browser.root_dir,directory])
    if not os.path.exists(full_path):
        return render_template('404.html', errorText='Invalid Directory')
    
    if not os.path.isdir(full_path):
        return render_template('404.html', errorText='Not a Directory')

    if file_browser.is_hidden(full_path):
        return render_template('404.html', errorText='Hidden Directory, Permission Denied')

    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        directory_path = Path(build_path([file_browser.root_dir,directory]))
        for root, dirs, files in os.walk(str(directory_path)):
            for file in files:
                file_path = build_path([root, file])
                zipf.write(file_path, str(Path(file_path).relative_to(directory_path)))
    memory_file.seek(0)
    return send_file(memory_file, attachment_filename=f'{directory.split("/")[-1]}.zip', as_attachment=True)



@main.route('/upload_files/', methods=['GET', 'POST'])
@main.route('/upload_files/<path:upload_dir>', methods=['GET', 'POST'])
@login_required
def upload_files(upload_dir=""): 
    file_browser = FileBrowser()
    full_path = build_path([file_browser.root_dir, upload_dir])
    if not os.path.exists(full_path):
        return render_template('404.html', errorText='Invalid Directory')
    
    if not os.path.isdir(full_path):
        return render_template('404.html', errorText='Not a Directory')

    if file_browser.is_hidden(full_path):
        return render_template('404.html', errorText='Hidden Directory, Permission Denied')

    files = request.files
    for item in files:
        uploaded_file = files.get(item)
        file_path = build_path([file_browser.root_dir, upload_dir, uploaded_file.filename])
        uploaded_file.save(file_path)

    return redirect("/browser/"+upload_dir)

@main.route('/create_dir/', methods=['POST'])
@main.route('/create_dir/<path:new_dir_parent>', methods=['POST'])
@login_required
def create_dir(new_dir_parent=""):
    file_browser = FileBrowser()
    full_path = build_path([file_browser.root_dir, new_dir_parent])
    if not os.path.exists(full_path):
        return render_template('404.html', errorText='Invalid Directory')
    
    if not os.path.isdir(full_path):
        return render_template('404.html', errorText='Not a Directory')

    if file_browser.is_hidden(full_path):
        return render_template('404.html', errorText='Hidden Directory, Permission Denied')
    
    new_dir_name = request.form['folder-name']

    if not new_dir_name.strip():
        return render_template('404.html', errorText='Directory name cannot be empty!!!')
    
    file_browser.create_new_directory(build_path([new_dir_parent, new_dir_name]))

    session['messages'] = file_browser.messages
    return redirect("/browser/"+new_dir_parent)

# @main.route('/copy_cut/', methods=['POST'])
@main.route('/copy_cut/<path:action>/<path:content_path>', methods=['GET'])
@login_required
def copy_cut(action="", content_path=""):
    if action not in ["copy", "cut"]:
         return render_template('404.html', errorText='Invalid Action')
    
    parent_dir =  Path(content_path).parent
    file_browser = FileBrowser()
    parent_full_path = build_path([file_browser.root_dir, str(parent_dir)])

    if not os.path.exists(parent_full_path):
        return render_template('404.html', errorText='Invalid file/directory path')

    if file_browser.is_hidden(parent_full_path):
        return render_template('404.html', errorText='Hidden Directory, Permission Denied')
    
    # print(f"{action} => {content_path}")
    session['copy_cut'] = {"action": action, "path": content_path}
    return redirect("/browser/"+str(parent_dir))

@main.route('/paste/<path:content_path>', methods=['GET'])
@login_required
def paste( content_path=""):
    parent_dir =  Path(content_path).parent
    file_browser = FileBrowser()
    parent_full_path = build_path([file_browser.root_dir, str(parent_dir)])

    if not os.path.exists(parent_full_path):
        return render_template('404.html', errorText='Invalid file/directory path')

    if file_browser.is_hidden(parent_full_path):
        return render_template('404.html', errorText='Hidden Directory, Permission Denied')
    
    source = session.get('copy_cut', {})
    if not source:
        return render_template('404.html', errorText='Unable to find source file or directory')

    file_browser.perform_copy_cut(source, content_path)

    session['messages'] = file_browser.messages
    session.pop('copy_cut', None)
    return redirect("/browser/"+str(parent_dir))