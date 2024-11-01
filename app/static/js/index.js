// --- Enum part
const FileType = {
    PDF: 1,
};

const Status = {
    Uploading: 1, // black
    Parsing: 2, // blue
    Completed: 3, // green
    Deleting: 4, // gray
    Failed: 9, // red
};

// --- General function
function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

function formatUA(timestamp) {
    timestamp = timestamp * 1000;
    const date = new Date(timestamp);

    // 提取月份、日期和年份
    const month = date.getMonth() + 1; // JavaScript 的月份從 0 開始
    const day = date.getDate();
    const year = date.getFullYear();

    // 提取小時、分鐘和秒數
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const seconds = date.getSeconds().toString().padStart(2, "0");

    // 判斷 AM/PM
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12; // 將 0 轉換為 12（12 小時制）

    // 格式化日期字串
    return `${month}/${day}/${year} ${hours}:${minutes}:${seconds} ${ampm}`;
}

function formatFT(fileType) {
    switch (fileType) {
        case FileType.PDF:
        default:
            return "PDF";
    }
}

function formatStatus(status) {
    switch (status) {
        case Status.Uploading:
            return "Uploading";

        case Status.Parsing:
            return "Parsing";

        case Status.Completed:
            return "Completed";

        case Status.Failed:
            return "Failed";

        default:
            return "Unknown";
    }
}

function isPDF(file) {
    return file.type === "application/pdf";
}

// --- Main function
function getFiles(fileId, success) {
    let url = "api/files";
    if (fileId) url += "/" + fileId;
    $.ajax({
        url,
        method: "GET",
        dataType: "json",
        success,
        error: function (xhr, status, error) {
            console.log({ xhr, status, error });
        },
    });
}

function addFile(data, success) {
    let url = "api/files";
    $.ajax({
        url,
        method: "POST",
        data,
        dataType: "json",
        success,
        error: function (xhr, status, error) {
            console.log({ xhr, status, error });
        },
    });
}

function delFile(fileId, success) {
    let url = "api/files/" + fileId;
    $.ajax({
        url,
        method: "DELETE",
        dataType: "json",
        success,
        error: function (xhr, status, error) {
            console.log({ xhr, status, error });
        },
    });
}

function renderData(srcData) {
    srcData = srcData.data;
    const tbody = $("#fileList tbody");
    if (!srcData || srcData.length == 0) {
        // TODO:: render 「No data found.」 hint.
        tbody.html(`<tr class="hint no_data">
                    <td colspan="7">No data found！</td>
                </tr>`);
        return;
    }

    tbody.empty();
    for (let i = 0; i < srcData.length; i++) {
        const aFileRec = srcData[i];
        const trEle = $(`<tr id="${aFileRec.id}" file_status="${aFileRec.status}">`)
            .append($('<td attr_name="id">').text(aFileRec.id))
            .append($('<td attr_name="fileName">').text(aFileRec.fileName))
            .append($('<td attr_name="uploadedAt">').text(formatUA(aFileRec.uploadedAt)))
            .append($('<td attr_name="fileType">').text(formatFT(aFileRec.fileType)))
            .append($('<td attr_name="status">').html(formatStatus(aFileRec.status)))
            .append($('<td attr_name="preview">').append($(`<button open_link="${aFileRec.parsedPath}" onclick="openPreview(this);">`).text("Open new Tab")))
            .append($('<td attr_name="deleteCB">').append($("<input>").attr("type", "checkbox")));
        tbody.append(trEle);

        // --- set btn status
        if (aFileRec.status != Status.Completed) {
            const previewBtn = $(`tr[id="${aFileRec.id}"] td[attr_name="preview"] button`);
            previewBtn.prop("disabled", true);
        }

        if (aFileRec.status == Status.Uploading || aFileRec.status == Status.Parsing) {
            const delCB = $(`tr[id="${aFileRec.id}"] td[attr_name="deleteCB"] input`);
            delCB.prop("disabled", true);
        }
    }
}

function loadFilesData() {
    getFiles(null, renderData);
}

function showPopup(msg) {
    $("#popup_msg").html(msg);
    document.getElementById("popupOverlay_hint").style.display = "flex";
}

function closePopup() {
    document.getElementById("popupOverlay_hint").style.display = "none";
}

function checkedAll(srcCheckbox) {
    $('input[type="checkbox"]:not(:disabled)').prop("checked", $(srcCheckbox).prop("checked"));
}

function delFiles() {
    const checkedBoxes = $('tbody input[type="checkbox"]:checked:not(:disabled)');
    if (checkedBoxes.length < 1) {
        showPopup("No file selected！");
        return;
    }
    checkedBoxes.each(function () {
        const fileId = $(this).closest("tr").attr("id");
        delFile(fileId, function (delRes) {
            loadFilesData();
        });
    });
}

function showUploadPopup() {
    $("#popupOverlay_upload").css("display", "flex");
}

function closeUploadPopup() {
    $("#popupOverlay_upload").hide();
}

// 清除上傳的檔案
function clearSelectedFile() {
    $("#fileInput").val("");
    $(`#uploaded_fileName`).text("");
}

function insertFile() {
    const fileInput = $("#fileInput")[0].files[0];
    if (!fileInput) {
        showPopup("Please select a file.");
        return;
    }

    if (!isPDF(fileInput)){
        showPopup("The document type does not support.");
        clearSelectedFile();
        return;
    }

    $.ajax({
        url: "api/files",
        type: "POST",
        data: fileInput,
        processData: false,
        contentType: 'application/json',
        data: JSON.stringify({
            fileName: fileInput.name,
            fileType: 1,
            status: 1
        }),
        success: function (response) {
            $(`#addBtn`).text("Please wait...");
            $(`#addBtn`).prop("disabled", true);

            loadFilesData();
            closeUploadPopup();
            uploadFile(response.data);
        },
        error: function (xhr, status, error) {
            let hint = "Request failed！";
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                hint = xhr.responseJSON.detail;
            }
            showPopup(hint);
            console.log({ xhr, status, error });

            clearSelectedFile();
        },
    });
}

function uploadFile(fileId) {
    const fileInput = $("#fileInput")[0].files[0];
    if (!fileInput) {
        showPopup("Please select a file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput);

    let url = "api/upload/" + fileId;
    $.ajax({
        url,
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        timeout: 30 * 60 * 1000, // 最多等半小時
        success: function (response) {
            loadFilesData();
            closeUploadPopup();
            parseFile(fileId);
        },
        error: function (xhr, status, error) {
            let fileName = $(`tr[id]="${fileId} td[attr_name="fileName"]"`).text();
            showPopup(fileName + "<br>File upload failed！");
            delFile(fileId, loadFilesData);
            console.log({ xhr, status, error });
        },
    }).always(function () {
        clearSelectedFile();

        // 上傳按鈕解禁
        $(`#addBtn`).text("Upload a new file");
        $(`#addBtn`).prop("disabled", false);
    });
}

function parseFile(fileId) {
    let url = "api/parse/" + fileId;

    $.ajax({
        url,
        type: "POST",
        timeout: 2 * 60 * 60 * 1000, // 最多等2小時
        processData: false,
        contentType: false,
        success: function (response) {
            const previewBtn = $(`tr[id="${fileId}"] td[attr_name="preview"] button`);
            previewBtn.prop("open_link", response.data)
            previewBtn.click(function(){
                window.open(this.open_link, "_blank");
            });
        },
        error: function (xhr, status, error) {
            let hint = "Pasred failed！";
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                hint = xhr.responseJSON.detail;
            }
            showPopup(hint);
            console.log({ xhr, status, error });
        },
    }).always(function () {
        loadFilesData();
    });
}

function selectUploadFile() {
    const fileInput = $("#fileInput")[0].files[0];
    if (!fileInput) return;

    if (!isPDF(fileInput)){
        showPopup("The document type does not support.");
        clearSelectedFile();
        return;
    }

    // 將檔名顯示在畫面上
    $(`#uploaded_fileName`).text(fileInput.name);
}

function openPreview(btn){
    const link = btn.getAttribute('open_link');
    if (link) window.open(link, "_blank");
}

function resetSystem(){
    if (!confirm("Are you sure you want to delete all files?")) return;
    $.ajax({
        url: 'api/reset',
        type: "DELETE",
        processData: false,
        contentType: false,
        success: function (response) {

        },
        error: function (xhr, status, error) {
        },
    }).always(function () {
        loadFilesData();
    });
}

$(document).ready(function () {
    loadFilesData();
});
