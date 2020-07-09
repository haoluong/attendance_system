import React, { Component } from 'react';
import Webcam from "react-webcam";
import History from '../../components/History/history';
import Header from "../../components/Header/header";
import { Form, Button, Segment, Modal, Image, Grid, Icon, Label } from 'semantic-ui-react';
import Axios from 'axios';


const divStyle = {
    padding: '40px',
    border: '0px solid white',
    margin: '0px 500px'
};
const header = {
    textAlign: 'center'
}
let icon_images = {
    color: 'red',
    display: 'none'
}
let icon_name = {
    color: 'red',
    display: 'none'
}
let icon_id = {
    color: 'red',
    display: 'none'
}
let icon_room = {
    color: 'red',
    display: 'none'
}
let icon_avatar = {
    color: 'red',
    display: 'none'
}

class NewStudent extends Component {
    constructor(props) {
        super(props);
        this.state = {
            std_id: '',
            std_name: '',
            std_room: '',
            avatar: '',
            images: [],
            imageCaptured: '',
            image_link: [],
            inputHidden: true,
            colorActive: '',
            openModal: false,
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
        let validate = true
        if (this.state.std_name === '') {
            this.setState({
                colorActive: 'red',
            })
            validate = false
            icon_name={display:'inline',color: 'red', right: "0%"}
        }
        else {
            icon_name={display:'none'}
        }
        if (this.state.std_id === '') {
            this.setState({
                colorActive: 'red'
            })
            validate = false
            icon_id={display:'inline',color: 'red', right: "0%"}
        }
        else {
            icon_id={display:'none'}
        }
        if (this.state.std_room === '') {
            this.setState({
                colorActive: 'red'
            })
            validate = false
            icon_room={display:'inline',color: 'red', right: "0%"}
        }
        else {
            icon_room={display:'none'}
        }
        if (this.state.avatar.length === '') {
            this.setState({
                colorActive: 'red'
            })
            validate = false
            icon_avatar={display:'inline',color: 'red', right: "0%"}
        }
        else {
            icon_avatar={display:'none'}
        }
        if (this.state.images.length === 0) {
            this.setState({
                colorActive: 'red'
            })
            validate = false
            icon_images={display:'inline',color: 'red', right: "0%"}
        }
        else {
            icon_images={display:'none'}
        }
        if(validate === true ) {
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
        let image_link_clone = this.state.image_link
        let images_clone = this.state.images
        image_link_clone.push(link_created)
        images_clone.push(link_created)
        this.setState({
            image_link: image_link_clone,
            avatar: link_created,
            images: images_clone,
            inputHidden: false
        })
    };
    btnAdd = (event) => {
        this.setState({
            openModal:true
        })
    }
    btnDone = (event) => {
        this.setState({
            openModal:false
        })
    }
    btnOK = (event) => {
        History.push("/studentlist")
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
                    <h5>Họ và tên: <h5 style={{color: "red", display:"inline"}}>*</h5><h5 style={icon_name}>Thiếu thông tin</h5></h5>
                    <Form.Input
                        required
                        fluid
                        id='form-input-first-name'
                        onChange={(event) => this.setState({ std_name: event.target.value })}
                    />
                    <h5>Mã số sinh viên: <h5 style={{color: "red", display:"inline"}}>*</h5><h5 style={icon_id}>Thiếu thông tin</h5></h5>
                    <Form.Input
                        required
                        fluid
                        onChange={(event) => this.setState({ std_id: event.target.value })}
                    />
                    <h5>Phòng: <h5 style={{color: "red", display:"inline"}}>*</h5><h5 style={icon_room}>Thiếu thông tin</h5></h5>
                    <Form.Input
                        required
                        fluid
                        onChange={(event) => this.setState({ std_room: event.target.value })}
                    />
                    <h5>Hình đại diện: <h5 style={{color: "red", display:"inline"}}>*</h5><h5 style={icon_avatar}>Thiếu thông tin</h5></h5>
                    <Form.Input
                        fluid
                        type="file"
                        id="avatar"
                        name="avatar"
                        onChange={this.onChange} />
                    <h5 type="text" id="file" hidden={this.state.inputHidden} style={{color:"green"}}>Đã chọn ảnh </h5>
                    <h5>Danh sách ảnh định danh:  <h5 style={{color: "red", display:"inline"}}>*</h5><h5 style={icon_images}>Thiếu thông tin</h5></h5>
                    <Form.Input
                        fluid
                        type="file"
                        id="images"
                        name="images"
                        multiple="multiple"
                        onChange={this.onMultipleChange} />
                    <h5 type="text" id="file" hidden={this.state.inputHidden} style={{color:"green"}}>Đã chọn ảnh </h5>
                    <Modal trigger={<Button onClick={this.btnAdd}>Thêm ảnh</Button>} basic size='small' open={this.state.openModal}>
                        {/* <Grid>
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
                        </Grid> */}

                        <Grid textAlign='center'>
                            <Grid.Row columns={1} >
                                <Grid.Column>
                                    <Webcam
                                        mirrored={true}
                                        audio={false}
                                        ref={this.setRef}
                                        screenshotFormat="image/jpeg"
                                        videoConstraints={videoConstraints} />
                                </Grid.Column>
                            </Grid.Row>
                            <Grid.Row columns={1} >
                                <Grid.Column>
                                    <Button onClick={this.btnCapture}>Chụp màn hình</Button>
                                </Grid.Column>
                            </Grid.Row>
                            <Grid.Row columns={5} >
                                <Grid.Column>
                                    <Image src={this.state.image_link[0]} size='medium' />
                                </Grid.Column>
                                <Grid.Column>
                                    <Image src={this.state.image_link[1]} size='large' />
                                </Grid.Column>
                                <Grid.Column>
                                    <Image src={this.state.image_link[2]} size='large' />
                                </Grid.Column>
                                <Grid.Column>
                                    <Image src={this.state.image_link[3]} size='large' />
                                </Grid.Column>
                                <Grid.Column>
                                    <Image src={this.state.image_link[4]} size='large' />
                                </Grid.Column>
                            </Grid.Row>
                            <Grid.Row>
                                <Grid.Column>
                                    <Button onClick={this.btnDone}>Hoàn thành</Button>
                                </Grid.Column>
                            </Grid.Row>
                        </Grid>
                    </Modal>
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
                        <Button color='blue' inverted onClick={this.btnOK}>OK</Button>
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
