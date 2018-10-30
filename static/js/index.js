$(function () {
    if (sessionStorage.getItem('indexlogo')) {
        if (sessionStorage.getItem('indexlogo') == 'show') {
            console.log(1);
            $("body").addClass("mini-sidebar");
            $(".light-logo").show();
            $('.navbar-brand span').hide();
        } else if (sessionStorage.getItem('indexlogo') == 'hide') {
            $("body").removeClass("mini-sidebar");
            $(".light-logo").hide();
            $('.navbar-brand span').show();
        }
    } else {
        sessionStorage.setItem('indexlogo', 'hide');
    }

    $(document).ready(function () {
        $(".text-muted").click(function () {
            if (sessionStorage.getItem('indexlogo') == 'hide') {
                 $(".light-logo").show();
                $("body").addClass("mini-sidebar");
                $('.navbar-brand span').hide();
                sessionStorage['indexlogo'] = 'show';
            } else if (sessionStorage.getItem('indexlogo') == 'show') {
                $(".light-logo").hide();
                $("body").removeClass("mini-sidebar");
                $('.navbar-brand span').show();
                sessionStorage['indexlogo'] = 'hide';
            }
        });
    });
});


