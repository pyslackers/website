import React from 'react';
import ReactDom from 'react-dom';
import $ from 'jquery';

import '../style/app.scss';
import 'semantic-ui-css/semantic.min';

import SlackInviteForm from './invite_form';
import setupMemberMap from './member_map';


$(() => {
    const mapContainer = $('#leaflet_container');
    $.get('/slack/api/timezones')
        .done(body => setupMemberMap(body))
        .fail(() => setupMemberMap({}))
        .always(() => mapContainer.removeClass('loading'));

    ReactDom.render(
        <SlackInviteForm/>,
        document.getElementById('slack_invite_form')
    );
});
