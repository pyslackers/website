import 'semantic-ui-css/semantic.min';
import $ from 'jquery';

import '../style/app.scss';

import './invite_form';
import setupMemberMap from './member_map';
import setupMemberChart from './member_history_chart';


$(() => {
    const mapContainer = $('#leaflet_container');
    $.get('/slack/api/timezones')
        .done(body => setupMemberMap(body))
        .fail(() => setupMemberMap({}))
        .always(() => mapContainer.removeClass('loading'));
});


$(() => {
    const chartContainer = $('#member_history_chart_container');
    $.get('/slack/api/monthlymemberships')
        .done(body => setupMemberChart(body))
        .fail(() => setupMemberChart({}))
        .always(() => chartContainer.removeClass('loading'));
});
