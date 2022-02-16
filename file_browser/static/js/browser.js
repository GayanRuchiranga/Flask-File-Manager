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
        if (document.getElementById("contextMenu").style.display == "block") {
            hideMenu();
        } else {
            var menu = document.getElementById("contextMenu");
            menu.querySelector('.download a').href = "/download_folder/" + target_dir;
            $('#fileUploadModal').find('form').attr('action', "/upload_files/" + target_dir)
            menu.style.display = 'block';
            menu.style.left = e.pageX + "px";
            menu.style.top = e.pageY + "px";
        }
    });

    $("#contextMenu .download").click(function() {
        $this = $(this);
        var target_dir = $this.href = "#"
        hideMenu();
    });

    $("#contextMenu .upload").click(function() {
        $this = $(this);
        $('#fileUploadModal').modal('show')
        hideMenu();
    });

});

function hideMenu() {
    var menu = document.getElementById("contextMenu");
    menu.style.display = "none";
};