function upfile(obj) {
    for (var i = 0; i < $(obj)[0].files.length; i++) {
        var form_data = new FormData();
        var file_info = $(obj)[0].files[i];
        form_data.append('file', file_info);
        $.ajax({
            url: "/project/upload/api/",
            type: "POST",
            cache: false,
            data: form_data,
            processData: false,
            contentType: false,
            success: function (data) {
                if (data['resole'] == 0) {
                    var file_name = "<div class=\"row\" style=\"margin-top: 18px><div class=\"col-md-7\"><span style=\"\n" +
                        "    \n" +
                        "\">" + data['file'] + "</span>" +
                        "                                                    </div><div class=\"col-md-3\"><span style=\"color: red;\">上传失败</span></div></div>";
                } else {
                    var file_name = "<div class=\"row\" style=\"margin-top: 18px\"><div class=\"col-md-7\"><input type=\"text\" name=\"file\" value=\"" + data['resole'] + "\" hidden><span style=\"\n" +
                        "   \n" +
                        "\">" + data['file'] + "</span><i class=\"mdi mdi-close-circle-outline\" onclick=\"del(this)\" title=\"" + data['resole'] + "\"></i>\n" +
                        "                                                    </div><div class=\"col-md-3\"><span style=\"color: green;\">上传成功</span></div></div>";
                }
                $(obj).after(file_name);
            }
        });
    }
}


function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = window.location.search.substr(1).match(reg); //匹配目标参数
    if (r != null) return unescape(r[2]);
    return null; //返回参数值
}