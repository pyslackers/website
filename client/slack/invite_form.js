import $ from 'jquery';

$(() => {
    $('#slack_invite_form')
        .form({
            fields: {
                email: {
                    identifier: 'email',
                    rules: [
                        {
                            type: 'email',
                            prompt: 'Please enter a valid email'
                        }
                    ]
                },
                accept_tos: {
                    identifier: 'accept_tos',
                    rules: [
                        {
                            type: 'checked',
                            prompt: 'You must agree to the terms'
                        }
                    ]
                }
            }
        });
});
