Dropzone.options.myDropzone = {
    autoProcessQueue: false,
    uploadMultiple: true,
    maxFilesize: 1024,
    parallelUploads: 1000,
    init: function() {
        var myDropzone = this;
        var upload_modal = document.getElementById('fileUploadModal');

        upload_modal.querySelector(".cancel-btn").addEventListener("click", function(e) {
            myDropzone.removeAllFiles();
        });

        upload_modal.querySelector(".close").addEventListener("click", function(e) {
            myDropzone.removeAllFiles();
        });

        upload_modal.querySelector(".upload-btn").addEventListener("click", function(e) {
            e.preventDefault();
            e.stopPropagation();
            myDropzone.processQueue();
        });
        this.on("processing", function(file) {
            this.options.url = $('#fileUploadModal').find('form').attr('action');
        });
    }
};

$(document).on('click','body',function(e){
    if (document.getElementById("directory-contextMenu").style.display == "block") {
        e.preventDefault();
        hideContextMenues();
    }
    if (document.getElementById("file-contextMenu").style.display == "block") {
        e.preventDefault();
        hideContextMenues();
    }
});

$(function() {
    $('[data-toggle="tooltip"]').tooltip()
})

$(function() {
    $('#view0_button').click(function() {

        $('#view1_container').css('display', 'none');
        $('#view0_container').css('display', 'block');
        $('#view0_button').prop("disabled", true);
        $('#view1_button').prop("disabled", false);


        const Http = new XMLHttpRequest();
        const url = '/changeView?view=0';
        Http.open("GET", url);
        Http.send();
    });
    $('#view1_button').click(function() {
        $('#view0_container').css('display', 'none');
        $('#view1_container').css('display', 'block');
        $('#view1_button').prop("disabled", true);
        $('#view0_button').prop("disabled", false);


        const Http = new XMLHttpRequest();
        const url = '/changeView?view=1';
        Http.open("GET", url);
        Http.send();
    });

    $('.directory').bind("contextmenu", function(e) {
        e.preventDefault();
        $this = $(this);
        var target_dir = decodeURIComponent($this.find('a')[0].href.split("/browser/")[1])
        console.log(target_dir)
        var directoryContextMenu = document.getElementById("directory-contextMenu");
        if (directoryContextMenu.style.display == "block") {
            hideContextMenues();
        } else {
            directoryContextMenu.querySelector('.download a').href = "/download_folder/" + target_dir;
            directoryContextMenu.querySelector('.copy a').href = "/copy_cut/copy/" + target_dir;
            directoryContextMenu.querySelector('.cut a').href = "/copy_cut/cut/" + target_dir;
            directoryContextMenu.querySelector('.paste a').href = "/paste/" + target_dir;
            $('#fileUploadModal').find('form').attr('action', "/upload_files/" + target_dir)
            directoryContextMenu.style.display = 'block';
            directoryContextMenu.style.left = e.pageX + "px";
            directoryContextMenu.style.top = e.pageY + "px";
        }
    });

    $("#directory-contextMenu .download").click(function() {
        $this = $(this);
        hideContextMenues();
    });
    $("#directory-contextMenu .copy").click(function() {
        $this = $(this);
        hideContextMenues();
    });
    $("#directory-contextMenu .cut").click(function() {
        $this = $(this);
        hideContextMenues();
    });
    $("#directory-contextMenu .paste").click(function() {
        $this = $(this);
        hideContextMenues();
    });

    $("#directory-contextMenu .upload").click(function() {
        $this = $(this);
        $('#fileUploadModal').modal('show')
        hideContextMenues();
    });


    $('.file').bind("contextmenu", function(e) {
        e.preventDefault();
        $this = $(this);

        var target_file = decodeURIComponent($this.find('a')[0].href.split("/download_file/")[1])
        if (document.getElementById("file-contextMenu").style.display == "block") {
            hideContextMenues();
        } else {
            var menu = document.getElementById("file-contextMenu");
            menu.querySelector('.download a').href = "/download_file/" + target_file;
            menu.querySelector('.copy a').href = "/copy_cut/copy/" + target_file;
            menu.querySelector('.cut a').href = "/copy_cut/cut/" + target_file;
            menu.querySelector('.paste a').href = "/paste/" + target_file;
            menu.style.display = 'block';
            menu.style.left = e.pageX + "px";
            menu.style.top = e.pageY + "px";
        }
    });

    $("#file-contextMenu .download").click(function() {
        $this = $(this);
        hideContextMenues();
    });
    $("#file-contextMenu .copy").click(function() {
        $this = $(this);
        hideContextMenues();
    });
    $("#file-contextMenu .cut").click(function() {
        $this = $(this);
        hideContextMenues();
    });
    $("#file-contextMenu .paste").click(function() {
        $this = $(this);
        hideContextMenues();
    });
    $('#newFolderModal').on('shown.bs.modal', function () {
        $('#folder-name').focus();
    }) 
});

function hideContextMenues() {
    var directoryContextMenu = document.getElementById("directory-contextMenu");
    directoryContextMenu.style.display = "none";

    var fileContextMenu = document.getElementById("file-contextMenu");
    fileContextMenu.style.display = "none";
};