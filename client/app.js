import $ from 'jquery';

import 'semantic-ui-css/semantic.min';
import './vendor/google_analytics.min';
import './style/app.scss';


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
