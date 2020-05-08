import React, { Component } from 'react'
import { Dropdown, Menu, Button, Container, Image } from 'semantic-ui-react'
import { Link } from "react-router-dom";
import History from '../History/history';

class Header extends Component {
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
        const { activeItem, fixed } = this.state

        return (
            <Menu secondary>
                <Menu.Item as='a' header>
                        <Image size='small' src='/Logo_KTX.png'/>
                    </Menu.Item>
                <Container centered>
                    
                    <Menu.Item id="" name="Trang chủ" onClick={this.handleItemClick} icon='home'/>

                    <Dropdown item text="Danh mục" >
                        <Dropdown.Menu>
                            <Dropdown.Item><Link to="/studentlist"><img src="" alt="" />Danh sách sinh viên</Link></Dropdown.Item>
                            <Dropdown.Item><Link to="/newstudent"><img src="" alt="" />Thêm sinh viên</Link></Dropdown.Item>
                            <Dropdown.Item><Link to="/studentlist"><img src="" alt="" />Camera</Link></Dropdown.Item>
                        </Dropdown.Menu>
                    </Dropdown>

                </Container>
                <Menu.Item position='right'>
                    <Button onClick={this.handleLogout} icon="shutdown" inverted color="blue"style={{ marginRight: '3.5em' }}/>
                </Menu.Item>
            </Menu>
        )
    }
}

export default Header;