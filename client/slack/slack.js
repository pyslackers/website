import 'semantic-ui-css/semantic.min';
import $ from 'jquery';

import '../style/app.scss';

import './invite_form';
import setupMemberMap from './member_map';


$(() => {
    const mapContainer = $('#leaflet_container');
    $.get('/slack/api/timezones')
        .done(body => setupMemberMap(body))
        .fail(() => setupMemberMap({}))
        .always(() => mapContainer.removeClass('loading'));
});
