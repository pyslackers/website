import React, { Component } from 'react';
import { Form, Message } from 'semantic-ui-react';
import $ from 'jquery';

import retrieveTaskResult from '../lib/task';


class SlackInviteForm extends Component {
  state = {
    email: '',
    acceptTOS: false,
    errors: {},
    loading: false,
    success: false,
  };

  onSubmit = async (e) => {
    e.preventDefault();

    const { email, acceptTOS } = this.state;

    this.setState({ errors: {}, loading: true, success: false });
    try {
      const inviteTask = await $.ajax({
        url: '/slack/',
        method: 'POST',
        data: {
          csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val(),
          email,
          accept_tos: acceptTOS,
        },
      });

      const taskResult = await retrieveTaskResult(inviteTask.task_id);
      const newState = (taskResult.error !== undefined)
        ? { errors: { email: [{ message: taskResult.error }] } }
        : { email: '', acceptTOS: false, success: true };
      this.setState(newState);
    } catch (error) {
      if ([400, 429].indexOf(error.status) !== -1) {
        this.setState({ errors: error.responseJSON });
      } else {
        alert('Sorry, something went wrong. Please refresh and try again.'); // eslint-disable-line
      }
    }
    this.setState({ loading: false });
  };

  formHasError = () => !$.isEmptyObject(this.state.errors);

  formatErrors = (errors) => {
    if (!this.formHasError()) {
      return [];
    }

    return Object.entries(errors).map(([key, errs]) => (
      `${key}: ${errs.map(e => e.message).join(',')}`
    ));
  };

  shouldButtonDisable = () => {
    const { email, acceptTOS } = this.state;
    return email === '' || !acceptTOS;
  };

  render() {
    const { loading, errors, acceptTOS, email, success } = this.state;
    return (
      <div>
        {success ?
          <Message
            header="See you in Slack!"
            content="Check your inbox, you should have an invite shortly"
            info
          /> : null
        }

        <Form loading={loading} error={this.formHasError()}>
          <Form.Input
            label="Email"
            placeholder="Email"
            type="email"
            onChange={e => this.setState({ email: e.target.value })}
            value={email}
            required
          />
          <Form.Checkbox
            label={<label>I agree to the <a href="/terms/">Terms and Code of Conduct</a></label>} // eslint-disable-line
            onChange={() => this.setState({ acceptTOS: !acceptTOS })}
            checked={acceptTOS}
            required
          />
          <Message
            header="Could you check something?"
            list={this.formatErrors(errors)}
            error
            content={
              <small>
                If this seems to be an error, please email us at&nbsp;
                <a href="mailto:pythondev.slack@gmail.com">pythondev.slack@gmail.com</a>
              </small>
            }
          />
          <Form.Button onClick={this.onSubmit} disabled={this.shouldButtonDisable()} primary>
            Submit
          </Form.Button>
        </Form>
      </div>
    );
  }
}

export default SlackInviteForm;
