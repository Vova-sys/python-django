function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');



$('document').ready(function () {
    $('span.comment_like').on('click', function () {
        let cl_id = $(this).attr('id');
        let object_comment = this;
        $.ajax({
            url: '/shop/add_like_ajax/',
            data: {"cl_id": cl_id, "csrfmiddlewaretoken": csrftoken},
            method: 'post',
            success: function (data) {
                $(object_comment).html(` Like: ${data['count_like']}`);
                let th = $(object_comment).parent();
                if (data['flag']) {
                    $(object_comment).attr('class', 'comment_like fa fa-star');
                    $(th).append(`<span class="col">${data['user']}</span>`)
                } else {
                    $(object_comment).attr('class', 'comment_like fa ');
                    for (var i = 0; i < $(th).children().length; i++) {
                        let item = $(th).children()[i];
                        if ($(item).html() == data['user']) {
                            $(th).children()[i].remove();
                            break
                        }
                    }
                }
            }
        });
    });
});