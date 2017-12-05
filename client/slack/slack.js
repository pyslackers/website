import 'semantic-ui-css/semantic.min';
import $ from 'jquery';

import '../style/app.scss';

import './invite_form';
import setupMemberMap from './member_map';


$(() => {
    let data = $('#slack_member_tz_count').data('timezones');
    if (data !== undefined) {
        // convert python list of tuples
        data = data
            .replace(/\(/g, '[')
            .replace(/\)/g, ']')
            .replace(/'/g, '"');
        setupMemberMap(JSON.parse(data));
    }
});
