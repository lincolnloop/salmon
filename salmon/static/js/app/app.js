(function ($) {
    var app = this.app || {};
    this.app = app;

    app.updateTimestamps = function () {
        $('#last-update').text(new Date().toLocaleTimeString());
        $("time.timeago").timeago();
    };

    app.updateContent = function (callback) {
        $.ajax({
            url: window.location.href,
            type: 'GET',
            data: { '_': new Date().getTime() },  // cache busting
            headers: {'X-PJAX': 'true'},
            success: function (data) {
                $('#content').html(data);
                app.updateTimestamps();
                if (callback) {
                    callback(arguments);
                }
            }
        });
    };
    $(document).ready(function () {
        app.updateTimestamps();
    });
})(jQuery);
