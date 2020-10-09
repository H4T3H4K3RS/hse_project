function datatables_init(selector = ".dt") {
    $(selector).DataTable({
        "columnDefs": [
            {"orderable": false, "targets": [0, -1]}
        ],
        "lengthMenu": [[3, 10, 50, 100, -1], [3, 10, 50, 100, "Все"]],
        "destroy": true,
        "stateSave": true,
        "language": {
            "emptyTable": "Нет данных",
            "info": "Показано с _START_ по _END_ из _TOTAL_ элементов",
            "infoEmpty": "Показано с 0 по 0 из 0 элементов",
            "infoFiltered": "(отфильтровано из _MAX_ элементов)",
            "infoPostFix": "",
            "thousands": ",",
            "lengthMenu": "Показать _MENU_ элементов",
            "loadingRecords": "Загрузка...",
            "processing": "Обработка...",
            "search": "Поиск:",
            "zeroRecords": "Не найдено",
            "paginate": {
                "first": "Первый",
                "last": "Последний",
                "next": "След.",
                "previous": "Пред."
            },
            "aria": {
                "sortAscending": ": активируйте для того, чтобы отсортировать по возрастанию",
                "sortDescending": ": активируйте для того, чтобы отсортировать по убыванию"
            }
        }
    });
}

function reload_account_links(username, id = "links_card") {
    $.ajax({
        url: window.reverse('api:account_links_username', username),
        type: 'GET',
        data: {},
        success: function (data, status) {
            document.getElementById(id).innerHTML = data;
            reload_account_folder(username);
        }
    });
}


function reload_account_folder(username, id = "folders_card") {
    $.ajax({
        url: window.reverse('api:account_folder_username', username),
        type: 'GET',
        data: {},
        success: function (data, status) {
            document.getElementById(id).innerHTML = data;
            reload_account_saved(username);
        }
    });
}


function reload_account_saved(username, id = "saved_card") {
    $.ajax({
        url: window.reverse('api:account_saved_username', username),
        type: 'GET',
        data: {},
        success: function (data, status) {
            document.getElementById(id).innerHTML = data;
            reload_account_rating(username);
        }
    });
}


function reload_account_rating(username, id = "user_rating") {
    $.ajax({
        url: window.reverse('api:account_rating', username),
        type: 'GET',
        data: {},
        success: function (data, status) {
            document.getElementById(id).innerHTML = data.rating;
            datatables_init();
            set_listeners();
            $(".preloader").delay(1000).fadeOut();
        }
    });
}

function reload_folder(folder_id, id = "links_card") {
    $.ajax({
        url: window.reverse('api:folder_view', folder_id),
        type: 'GET',
        data: {},
        success: function (data, status) {
            document.getElementById(id).innerHTML = data;
            datatables_init();
            set_listeners();
        }
    });
}


function reload_index(id = "links_card") {
    $.ajax({
        url: window.reverse('api:index_view'),
        type: 'GET',
        data: {},
        success: function (data, status) {
            document.getElementById(id).innerHTML = data;
            datatables_init();
            set_listeners();
        }
    });
}


function reload_search(id = "search_card") {
    let url = window.reverse('api:search_view') + '?q=' + $('[name="hidden_query"]').val().split(" ").join("+");
    $.ajax({
        url: url,
        type: 'GET',
        data: {},
        success: function (data, status) {
            document.getElementById(id).innerHTML = data;
            datatables_init();
            set_listeners();
        }
    });
}


function reload(type, reloader, id = "content") {
    $(".preloader").fadeIn();
    if (type === 'account') {
        reload_account_links(reloader, "links_card");
    } else if (type === 'folder') {
        reload_folder(reloader, "links_card");
    } else if (type === 'index') {
        reload_index("links_card");
        $(".preloader").delay(1000).fadeOut();
    } else if (type === 'search') {
        reload_search("search_card");
        $(".preloader").delay(1000).fadeOut();
    }

}


function delete_link(link_id, type, reloader) {
    $.ajax({
        url: window.reverse('link_delete', link_id),
        type: 'GET',
        beforeSend: function () {
            toastr.info("Удаление ссылки");
        },
        success: function (data, status) {
            toastr.clear();
            toastr.success(data.data);
            reload(type, reloader);
        }
    });
}


function favourite_save(link_id, type, reloader, id = 'messages') {
    $.ajax({
        url: window.reverse('favourite_save', link_id),
        type: 'GET',
        beforeSend: function () {
            toastr.info("Добавление ссылки в сохранённое");
        },
        success: function (data, status) {
            toastr.clear();
            toastr.success(data.data);
            reload(type, reloader);
        }
    });
}


function favourite_save_alt(link_id, type, reloader, id = 'messages') {
    $.ajax({
        url: window.reverse('favourite_save_alt', link_id),
        type: 'GET',
        beforeSend: function () {
            toastr.info("Добавление ссылки в сохранённое");
        },
        success: function (data, status) {
            toastr.clear();
            toastr.success(data.data);
            reload(type, reloader);
        }
    });
}


function vote(link_id, vote, type, reloader, id = 'messages') {
    $.ajax({
        url: window.reverse('link_vote', link_id, vote),
        type: 'GET',
        beforeSend: function () {
            toastr.info("Отправка голоса");

        },
        success: function (data, status, xhr) {
            toastr.clear();
            // console.log(data);
            if (xhr.status === 200) {

            }
            if (xhr.status === 203)
                toastr.success(data.data);
            if (xhr.status === 202)
                toastr.warning(data.data);
            if (xhr.status === 208)
                toastr.error(data.data);
            // console.log(xhr.status);
            reload(type, reloader);
        }
    });
}


function delete_favourite(link_id, type, reloader) {
    $.ajax({
        url: window.reverse('favourite_delete', link_id),
        type: 'GET',
        beforeSend: function () {
            toastr.info("Удаление ссылки из сохранённого");
        },
        success: function (data, status) {
            toastr.clear();
            toastr.success(data.data);
            reload(type, reloader);
        }
    });
}


function delete_folder(folder_id, type, reloader, id = 'messages') {
    $.ajax({
        url: window.reverse('folder_delete', folder_id),
        type: 'GET',
        beforeSend: function () {
            toastr.info("Удаление подборки");
        },
        success: function (data, status) {
            toastr.clear();
            toastr.success(data.data);
            reload(type, reloader);
        }
    });
}


function set_avatar(id, imgselector = ".avatar") {
    $.ajax({
        url: window.reverse('api:account_avatar', id),
        type: 'GET',
        beforeSend: function () {
            $(".preloader").fadeIn();
            toastr.info("Обновление аватара");
        },
        success: function (data, status) {
            toastr.clear();
            toastr.success("Аватар обновлён");
            var avatars = $(imgselector);
            console.log(avatars);
            avatars.attr('src', avatars.attr('src').replace(data.before, data.after));
            $(".preloader").fadeOut();
        }
    });
}


function new_key(selector = "#api_key input") {
    $.ajax({
        url: window.reverse('api:account_new_api_key'),
        type: 'GET',
        beforeSend: function () {
            $(".preloader").fadeIn();
            toastr.info("Обновление API-ключа");
        },
        success: function (data, status) {
            toastr.clear();
            toastr.success("API-ключ обновлён");
            var key = $(selector);
            key.val(data.data);
            $("#bot_link").attr("href", "https://t.me/hse_linkit_bot?start=" + data.data);
            $(".preloader").fadeOut();
        }
    });
}


function set_listeners() {
    $('.delete_link_btn').click(function () {
        // console.log($(this).data('id'), $(this).data('type'), $(this).data('data'));
        delete_link($(this).data('id'), $(this).data('type'), $(this).data('data'));
    });
    $('.favourite_delete_btn').click(function () {
        // console.log($(this).data('id'), $(this).data('type'), $(this).data('data'));
        delete_favourite($(this).data('id'), $(this).data('type'), $(this).data('data'));
    });
    $('.favourite_add_btn').click(function () {
        // console.log($(this).data('id'), $(this).data('type'), $(this).data('data'));
        favourite_save($(this).data('id'), $(this).data('type'), $(this).data('data'));
    });
    $('.favourite_add_alt_btn').click(function () {
        // console.log($(this).data('id'), $(this).data('type'), $(this).data('data'));
        favourite_save_alt($(this).data('id'), $(this).data('type'), $(this).data('data'));
    });
    $('.vote_btn').click(function () {
        // console.log($(this).data('id'), $(this).data('type'), $(this).data('data'));
        vote($(this).data('id'), $(this).data('vote'), $(this).data('type'), $(this).data('data'));
    });
    $('.delete_folder_btn').click(function () {
        // console.log($(this).data('id'), $(this).data('type'), $(this).data('data'));
        delete_folder($(this).data('id'), $(this).data('type'), $(this).data('data'));
    });
    $('[data-toggle="tooltip"]').click(function () {
        $('[data-toggle="tooltip"]').tooltip("hide");

    });
    $('[data-toggle="tooltip"]').tooltip();
    $(".redirect").on('click', function (event) {
        toastr.success("Войдите для того, чтобы выполнить данное действие");
        setTimeout(function () {
            window.location.href = window.reverse('account:login');
        }, 3000);
    });
    $('[data-change="avatar"]').click(function () {
        set_avatar($(this).data('data'));
    });
    $('[data-change="api_key"] a').on('click', function (event) {
        event.preventDefault();
    });
    $('[data-change="api_key"]').click(function (event) {
        new_key();
    });
}

datatables_init();
$(document).ready(function () {
    set_listeners();
    $(".bs-switch [type='checkbox']").bootstrapSwitch();
    $(".btn-hide a").on('click', function (event) {
        event.preventDefault();
        if ($('.closed .input-hide').attr("type") == "text") {
            $('.closed .input-hide').attr('type', 'password');
            $('.closed .btn-hide i').addClass("fa-eye-slash");
            $('.closed .btn-hide i').removeClass("fa-eye");
        } else if ($('.closed .input-hide').attr("type") == "password") {
            $('.closed .input-hide').attr('type', 'text');
            $('.closed .btn-hide i').removeClass("fa-eye-slash");
            $('.closed .btn-hide i').addClass("fa-eye");
        }
    });
    $(".btn-copy a").on('click', function (event) {
        event.preventDefault();
        $('.copied .btn-copy').addClass("btn-success");
        var dummy = document.createElement("textarea");
        var copyText = $(".input-copy").val();
        document.body.appendChild(dummy);
        dummy.value = copyText;
        dummy.select();
        const successful = document.execCommand("copy");
        document.body.removeChild(dummy);
        document.execCommand("copy");
        toastr.success("API-ключ скопирован.")
    });

});
toastr.options.closeButton = true;
toastr.options.showMethod = 'slideDown';
toastr.options.hideMethod = 'slideUp';
toastr.options.closeMethod = 'slideUp';
toastr.options.progressBar = true;
$("#delete_account_button").click(function () {
    Swal.fire({
        title: 'Вы уверены, что хотите удалить аккаунт?',
        text: "Вы не сможете восстановить его данные после удаления.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#f62d51',
        cancelButtonColor: '#7460ee',
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена'
    }).then((result) => {
        if (result.value) {
            toastr.success("Аккаунт был успешно удалён.");
            window.location.href = window.reverse('account:delete');
        }
    })
});