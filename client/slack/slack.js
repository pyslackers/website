import 'semantic-ui-css/semantic.min';
import $ from 'jquery';

import '../style/app.scss';

import './invite_form';
import setupMemberMap from './member_map';


$(() => {
    let data = JSON.parse($('#slack_member_tz_count').html());
    setupMemberMap(data);
});
