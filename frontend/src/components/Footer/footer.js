import React, { Component } from 'react'
import { Container, Segment, Grid, List, Divider, Image } from 'semantic-ui-react'
import { Link } from "react-router-dom";
import History from '../History/history';

// const style = {
//     position: sticky,
//     bottom: 0,
//     left: 0,
//     right: 0
// }
class Footer extends Component {
    state = { activeItem: '' }

    handleItemClick = (e, { id }) => {
        this.setState({ activeItem: id })
        History.push('/' + id)
    }
    handleLogout() {
        localStorage.clear();
        History.push('/login');
    }
    render() {
        const { sticky } = this.state

        return (
            <Segment inverted vertical style={{ margin: '12em 0em 0em', padding: '2em 0em', backgroundColor:'CornflowerBlue'}} >
                <Container textAlign='center'>
                    {/* <Image centered size='mini' src='/Logo_KTX.png' backgroundColor='white' /> */}
                    <p>Địa chỉ: 497 Hòa Hảo, Phường 7, Quận 10, TP.HCM</p>
                    <p>Điện thoại: 028.39 573 946</p>
                    <List horizontal inverted divided link size='small'>
                        <List.Item as='a' href='#'>
                            Site Map
          </List.Item>
                        <List.Item as='a' href='#'>
                            Contact Us
          </List.Item>
                        <List.Item as='a' href='#'>
                            Terms and Conditions
          </List.Item>
                        <List.Item as='a' href='#'>
                            Privacy Policy
          </List.Item>
                    </List>
                </Container>
            </Segment>

        )
    }
}

export default Footer;