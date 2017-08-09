$(document).ready(function () {
    $('.message .close')
        .on('click', function () {
            $(this).closest('.message').transition('fade');
        });

    $('.ui.checkbox').checkbox();
    $('.ui.dropdown').dropdown();
});