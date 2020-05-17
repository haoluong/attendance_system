import React, { Component } from 'react';
import Header from "../../components/Header/header";
import { Form, Button, Segment, Modal } from 'semantic-ui-react';
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
            image: null,
            openModalSuccess: false,
            openModalError: false
        }
        this.onChange = this.onChange.bind(this);
    }
    handleSubmit = event => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('image', this.state.image)
        formData.append('std_id', this.state.std_id)
        formData.append('std_name', this.state.std_name)
        formData.append('std_room', this.state.std_room)
        const student = {
            std_id: this.state.std_id,
            std_name: this.state.std_name,
            std_room: this.state.std_room
        };
        Axios.post('http://127.0.0.1:9999/newstudent', formData, { headers: { 'content-type': 'multipart/form-data' } })
            .then((res) => {
                if (res.data.status === true) {
                    this.setState({ openModalSuccess: true})
                }
                else {
                    this.setState({openModalError: true})
                }
            }).catch((error) => {
                console.log(error)
            });
    }

    closeModal = () => {
        this.setState({ openModalSuccess: false, openModalError: false })
        window.location.reload();
    }

    onChange(e) {
        let link_created = e.target.files[0] ? URL.createObjectURL(e.target.files[0]) : ''
        this.setState({
          image:e.target.files[0],
        });
    }
    // uploadFile = event => {
    //     event.preventDefault();
    //     const formData = new FormData();
    //     formData.append('image', event.target.files[0])
    //     Axios.post(
    //         'http://127.0.0.1:9999/newstudent',
    //         formData,
    //         { headers: { 'content-type': 'multipart/form-data' } }
    //     ).then((res) => {
    //     }).catch((error) => {
    //         console.log(error)
    //     });
    // }

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
                        label='Hình ảnh'
                        type="file"
                        id="file"
                        name="filename"
                        multiple="multiple"
                        onChange= {this.onChange}/>
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
                <Modal open={this.state.openModalSuccess} onClose={this.closeModal} basic size='small'>
                    {/* <Modal.Header icon='archive' content='Archive Old Messages' /> */}
                    <Modal.Content>
                        <p>Đăng ký thông tin sinh viên thành công!</p>
                    </Modal.Content>
                    <Modal.Actions>
                        <Button color='blue' inverted onClick={this.closeModal}>OK</Button>
                    </Modal.Actions>
                </Modal>
                <Modal open={this.state.openModalError} onClose={this.closeModal} basic size='small'>
                    {/* <Modal.Header icon='archive' content='Archive Old Messages' /> */}
                    <Modal.Content>
                        <p>Mã số sinh viên đã tồn tại. Vui lòng đăng ký thông tin khác!</p>
                    </Modal.Content>
                    <Modal.Actions>
                        <Button color='blue' inverted onClick={this.closeModal}>OK</Button>
                    </Modal.Actions>
                </Modal>
            </Form>
        )
    };
}
export default NewStudent
