$(document).ready(function () {
    $('#invite_form')
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
                }
            }
        });
});