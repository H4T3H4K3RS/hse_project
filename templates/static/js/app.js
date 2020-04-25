$(function () {
    var $password = $(".form-control[type='password']");
    var $passwordAlert = $(".password-alert");
    var $requirements = $(".requirements");
    var leng, bigLetter, num, specialChar;
    var $leng = $(".leng");
    var $bigLetter = $(".big-letter");
    var $num = $(".num");
    var $specialChar = $(".special-char");
    var specialChars = "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~";
    var numbers = "0123456789";

    $requirements.addClass("wrong");
    $password.on("focus", function () {
        $passwordAlert.show();
    });

    $password.on("input blur", function (e) {
        var el = $(this);
        var val = el.val();
        $passwordAlert.show();

        if (val.length < 8) {
            leng = false;
        } else if (val.length > 7) {
            leng = true;
        }


        if (val.toLowerCase() == val) {
            bigLetter = false;
        } else {
            bigLetter = true;
        }

        num = false;
        for (var i = 0; i < val.length; i++) {
            for (var j = 0; j < numbers.length; j++) {
                if (val[i] == numbers[j]) {
                    num = true;
                }
            }
        }

        specialChar = false;
        for (var i = 0; i < val.length; i++) {
            for (var j = 0; j < specialChars.length; j++) {
                if (val[i] == specialChars[j]) {
                    specialChar = true;
                }
            }
        }

        if (leng === false && bigLetter === false && num === false && specialChar === false) {
            $(':submit').prop('disabled', true);
        } else {
            $(':submit').prop('disabled', false);
        }
    });
});
(($) => {

    class Toggle {

        constructor(element, options) {

            this.defaults = {
                icon: 'fa-eye'
            };

            this.options = this.assignOptions(options);

            this.$element = element;
            this.$button = $(`<button class="btn-toggle-pass" type="button"><i class="fa ${this.options.icon}"></i></button>`);

            this.init();
        };

        assignOptions(options) {

            return $.extend({}, this.defaults, options);
        }

        init() {

            this._appendButton();
            this.bindEvents();
        }

        _appendButton() {
            this.$element.after(this.$button);
        }

        bindEvents() {

            this.$button.on('click touchstart', this.handleClick.bind(this));
        }

        handleClick() {

            let type = this.$element.attr('type');

            type = type === 'password' ? 'text' : 'password';

            this.$element.attr('type', type);
            this.$button.toggleClass('active');
            $(":input[type=password]").click();
        }
    }

    $.fn.togglePassword = function (options) {
        return this.each(function () {
            new Toggle($(this), options);
        });
    }

})(jQuery);

$(document).ready(function () {
    $(':password').togglePassword();
});
$('#password1').popover({
    trigger: 'focus',
    html: true,
    title: 'Ваш пароль должен содержать:',
    content: "&mdash; минимум 8 символов<br>&mdash; минимум 1 ПРОПИСНУЮ букву<br>&mdash; минимум 1 строчную букву<br>&mdash; минимум 1 специальный символ<br>&mdash; не простой пароль"
}).click(function () {
    setTimeout(function () {
        $(':password').popover('hide');
    }, 2000);
});

$(':submit').hover(function () {
    $('#password1').popover('show');
    setTimeout(function () {
        $('#password1').popover('hide');
    }, 2000);
});