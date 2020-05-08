import React, { Component } from 'react';
import Header from "../../components/Header/header";
import { Table, Form, Button, Label, Menu, Icon, Segment } from 'semantic-ui-react';
import History from '../../components/History/history';
import Axios from 'axios';


const divStyle = {
    padding: '40px',
    border: '0px solid white',
    margin: '0px 500px'
};
const header = {
    textAlign: 'center'
}

class NewStudent extends Component {
    constructor(props) {
        super(props);
        this.state = {
            std_id: '',
            std_name: '',
            std_room: '',
            avatar: null,
            images: null
        }
        this.onChange = this.onChange.bind(this);
        this.onMultipleChange = this.onMultipleChange.bind(this);
    }

    handleSubmit = event => {
        event.preventDefault();
        const formData = new FormData();
        for (var x = 0; x < this.state.images.length; x++) {
            formData.append("image" + x, this.state.images[x]);
        }
        formData.append('avatar', this.state.avatar)
        formData.append('num_image', this.state.images.length)
        formData.append('std_id', this.state.std_id)
        formData.append('std_name', this.state.std_name)
        formData.append('std_room', this.state.std_room)
        console.log(formData)
        Axios.post('http://127.0.0.1:9999/newstudent', formData,{ headers: { 'content-type': 'multipart/form-data' } })
            .then((res) => {
                if (res.data.status === true) {
                    History.push('/message')
                }
                else {
                    console.log(false)
                }
            }).catch((error) => {
                console.log(error)
            });
    }

    onChange(e) {
        let link_created = e.target.files[0] ? URL.createObjectURL(e.target.files[0]) : ''
        this.setState({
          avatar:e.target.files[0],
        });
    }

    onMultipleChange(e) {
        let link_created = e.target.files[0] ? URL.createObjectURL(e.target.files[0]) : ''
        this.setState({
          images:e.target.files,
        });
    }

    render() {
        return (
            <Form size='large'>
                <Header />
                <Segment style={divStyle}>
                    <h1 style={header}>Thêm sinh viên</h1>
                    <Form.Input
                        fluid
                        label='Họ và tên'
                        id='form-input-first-name'
                        onChange={(event) => this.setState({ std_name: event.target.value })}
                    />
                    <Form.Input
                        fluid
                        label='Mã số sinh viên'
                        onChange={(event) => this.setState({ std_id: event.target.value })}
                    />
                    <Form.Input
                        fluid
                        label='Phòng'
                        onChange={(event) => this.setState({ std_room: event.target.value })}
                    />
                    <Form.Input
                        fluid
                        label='Avatar'
                        type="file"
                        id="avatar"
                        name="avatar"
                        onChange= {this.onChange}/>
                    <Form.Input
                        fluid
                        label='Danh sách ảnh định danh'
                        type="file"
                        id="images"
                        name="images"
                        multiple="multiple"
                        onChange= {this.onMultipleChange}/>
                    {/* <Form.Checkbox
                    label='I agree to the Terms and Conditions'
                    error={{
                        content: 'You must agree to the terms and conditions',
                        pointing: 'left',
                    }}
                /> */}
                    <Segment basic textAlign={"center"}>
                        <Button style={{ textAlign: "center" }} color='blue' onClick={this.handleSubmit}>Xác nhận</Button>
                    </Segment>
                </Segment>
            </Form>
        )
    };
}
export default NewStudent
