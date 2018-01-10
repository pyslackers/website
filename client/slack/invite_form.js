import React, { Component } from 'react';
import { Form, Message } from 'semantic-ui-react';
import $ from 'jquery';

import { retrieveTaskResult } from '../lib/task';


class SlackInviteForm extends Component {
    state = {
        email: '',
        acceptTos: false,
        errors: {},
        loading: false,
        success: false,
    };

    render() {
        const { loading, errors, acceptTos, email, success } = this.state;
        return (
            <div>
                { success
                    ? <Message info header='See you in slack!'
                               content='Check your inbox, you should have an invite shortly' />
                    : null }

                <Form loading={loading} error={this.formHasError()}>
                    <Form.Input label='Email' placeholder='Email' type='email'
                                onChange={ e => this.setState({ email: e.target.value }) }
                                value={ email } required />
                    <Form.Checkbox label={ <label>I agree to the <a href="/terms/">Terms and Code of Conduct</a></label> }
                                   onChange={ () => this.setState({ acceptTos: !acceptTos }) }
                                   checked={ acceptTos } required />
                    <Message error header='Could you check something?' list={ this.formatErrors(errors) }
                             content={
                                 <small>
                                     If this seems to be an error, please email us at&nbsp;
                                     <a href="mailto:pythondev.slack@gmail.com">pythondev.slack@gmail.com</a>
                                 </small>} />
                    <Form.Button onClick={ this.onSubmit } disabled={ this.shouldButtonDisable() } primary>
                        Submit
                    </Form.Button >
                </Form>
            </div>
        );
    }

    onSubmit = async (e) => {
        e.preventDefault();

        const { email, acceptTos } = this.state;

        this.setState({ errors: {}, loading: true, success: false });
        try {
            const inviteTask = await $.ajax({
                url: '/slack/',
                method: 'POST',
                data: {
                    csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
                    email: email,
                    accept_tos: acceptTos,
                },
            });

            const taskResult = await retrieveTaskResult(inviteTask.task_id);
            const newState = (taskResult.error !== undefined)
                ? { errors: { email: [{message: taskResult.error}] } }
                : { email: '', acceptTos: false, success: true };
            this.setState(newState);
        } catch (e) {
            if ([400, 429].indexOf(e.status) !== -1) {
                this.setState({ errors: e.responseJSON });
            } else {
                console.error('Unknown error:', e);
                alert('Sorry, something went wrong. Please refresh and try again.');
            }
        }
        this.setState({ loading: false });
    };

    shouldButtonDisable = () => {
        const { email, acceptTos } = this.state;
        return email === '' || !acceptTos;
    };

    formHasError = () => {
        return Object.keys(this.state.errors).length > 0 && this.state.errors.constructor === Object;
    };

    formatErrors = (errors) => {
        if (!this.formHasError()) {
            return [];
        }

        return Object.entries(errors).map(([ key, errors ]) => (
            `${key}: ${errors.map(e => e.message).join(',')}`
        ))
    };
}

export default SlackInviteForm;
