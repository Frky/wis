
var cover_selected = function(iid) {
    $("td", "table").each(function() {
        if ($(this).attr("data-iid") != iid) {
            $(".cover", this).removeClass("active");
            $(".cover", this).addClass("hidden");
        } else {
            $(".cover", this).addClass("active");
            $(".cover", this).removeClass("hidden");
        }
    });
}

var select_cover = function(iid) {
    jQuery.ajax({
        url: URL_SELECT_COVER,
        data: { iid: iid, gid: $("#gid").val()},
        success: function() { cover_selected(iid) },
    });
}

$(document).ready(function() {
    $("td", "table").each(function() {
        $(this).hover(
            function() {
                $(".cover", this).removeClass("hidden");
            },
            function() {
                if ($(".cover", this).hasClass("active"))
                    return;
                $(".cover", this).addClass("hidden");
            }
        );
        $(this).click(function() {
            select_cover($(this).attr("data-iid"));
        });
    });
});
