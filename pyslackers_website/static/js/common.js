$(() => {
    $('.message .close')
        .on('click', function onMessageClose() {
            $(this).closest('.message').transition('fade');
        });

    $('.ui.checkbox').checkbox();
    $('.ui.dropdown').dropdown();

    $('.special.cards .image').dimmer({
        on: 'hover',
    });
});
