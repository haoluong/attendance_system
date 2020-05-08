import React, { Component } from 'react'
import { Button, Grid, Form, Header, Image, Segment, Message } from 'semantic-ui-react'
import Axios from 'axios'
import History from '../../components/History/history';

class Login extends Component {
    constructor(props) {
        super(props);
        this.state = {
            username: '',
            password: ''
        }

    }
    handleSubmit = event => {
        event.preventDefault();

        const user = {
            username: this.state.username,
            password: this.state.password
        };
        Axios.post('http://127.0.0.1:9999/login', user)
            .then((res) => {
                if (res.data["success"]) {
                    History.push('/')
                }
                else {
                    console.log(false)
                }
            }).catch((error) => {
                console.log(error)
            });
    }
    render() {
        return (
            <Grid textAlign='center' style={{ height: '100vh' }}>
            <Grid.Column style={{ maxWidth: 450}}>
                <Image src='/Logo_KTX.png' style={{margin:50}}/>
              <Form size='large'>
                <Segment>
                  <Form.Input fluid icon='user' iconPosition='left' placeholder='Tên đăng nhập' onChange={(event) => this.setState({ username: event.target.value })} />
                  <Form.Input fluid icon='lock' iconPosition='left' placeholder='Mật khẩu' type='password' onChange={(event) => this.setState({ password: event.target.value })}/>
                  <Button color='blue' fluid size='large' onClick={this.handleSubmit}>Đăng nhập</Button>
                </Segment>
              </Form>
              {/* <Message>
                New to us? <a href='/home'>Sign Up</a>
              </Message> */}
            </Grid.Column>
          </Grid>
        )
    }
}

export default Login