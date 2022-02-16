import tempfile
from flask import Blueprint, render_template, request, send_file, redirect, session, jsonify, flash
from flask_login import login_required, current_user
from browse import FileBrowser, build_path
import os
from io import BytesIO
import zipfile
import time

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
    file_browser.changeDirectory(relative_path, session.get("prev_path",""))
    session["prev_path"] = file_browser.current_dir

    return render_template('browser.html',
    errors = file_browser.errors,
    breadcrumbs = file_browser.breadcrumbs,
    dirs_info = file_browser.directories_info,
    files_info = file_browser.files_info,
    default_view = int(session.get("default_view", 0)))


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
        for root, dirs, files in os.walk(build_path([file_browser.root_dir,directory])):
            for file in files:
                zipf.write(os.path.join(root, file), file)
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
    