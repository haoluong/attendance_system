import React, { Component } from 'react';
import Webcam from "react-webcam";
import Header from "../../components/Header/header";
import { Form, Button, Segment, Modal, Image, Grid } from 'semantic-ui-react';
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
            avatar: '',
            images: null,
            imageCaptured: '',
            openCam: false,
            camHidden: false,
            imgHidden: true,
            image_link: ''
        }
        this.onChange = this.onChange.bind(this);
        this.onMultipleChange = this.onMultipleChange.bind(this);
    }
    setRef = webcam => {
        this.webcam = webcam;
    };

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
        Axios.post('http://127.0.0.1:9999/newstudent', formData, { headers: { 'content-type': 'multipart/form-data' } })
            .then((res) => {
                if (res.data.status === true) {
                    this.setState({ openModalSuccess: true })
                }
                else {
                    this.setState({ openModalError: true })
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
            avatar: e.target.files[0],
        });
    }

    onMultipleChange(e) {
        let link_created = e.target.files[0] ? URL.createObjectURL(e.target.files[0]) : ''
        this.setState({
            images: e.target.files,
        });
    }

    btnCapture = (event) => {
        event.preventDefault();
        let link_created = this.webcam.getScreenshot();
        this.setState({
            image_link: link_created,
            avatar: link_created,
            images: [link_created]
        })
    };
    btnAdd = (event) => {
        this.setState({
            openCam: true
        })
    }

    render() {
        const videoConstraints = {
            width: 640,
            height: 480,
            facingMode: "user"
        };
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
                        label='Hình đại diện'
                        type="file"
                        id="avatar"
                        name="avatar"
                        onChange={this.onChange} />
                    <Form.Input
                        fluid
                        label='Danh sách ảnh định danh'
                        type="file"
                        id="images"
                        name="images"
                        multiple="multiple"
                        onChange={this.onMultipleChange} />
                    <Modal trigger={<Button>Thêm ảnh</Button>} basic size='small'>
                        <Grid>
                            <Grid.Row stretched >
                                <Grid.Column width={7}>
                                    <Webcam
                                        mirrored={true}
                                        audio={false}
                                        ref={this.setRef}
                                        screenshotFormat="image/jpeg"
                                        videoConstraints={videoConstraints} />
                                </Grid.Column>
                                <Grid.Column width={8}>
                                    <Image src={this.state.image_link} size='large' />
                                </Grid.Column>
                            </Grid.Row>
                            <Grid.Row columns={2} textAlign='center'>
                                <Grid.Column width={8}>
                                    <Button onClick={this.btnCapture}>Chụp màn hình</Button>
                                </Grid.Column>
                            </Grid.Row>
                        </Grid>
                    </Modal>
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
