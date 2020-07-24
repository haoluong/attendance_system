import React, { Component } from 'react';
import Webcam from "react-webcam";
import Header from "../../components/Header/header";
import Footer from "../../components/Footer/footer"
import { Form, Modal, Button, Image, Input, Grid, Table } from 'semantic-ui-react'
import Axios from 'axios';

const SERVER = '127.0.0.1:9999'
class Home extends Component {
    constructor(props) {
        super(props);
        this.state = {
            student: {
                std_name: '',
                std_id: '',
                std_room: '',
                avatar: 'bk1.png'
            },
            image_link: '',
            imageCaptured: '',
            camHidden: false,
            imgHidden: true, 
            btnDisable: true
        }
    }
    setRef = webcam => {
        this.webcam = webcam;
    };

    recog_image = () => {
        const formData = new FormData();
        formData.append('image', this.state.imageCaptured)
        Axios.post(
            'http://'+SERVER+'/attend',
            formData,
            { headers: { 'content-type': 'multipart/form-data' } }
        ).then((res) => {
            let prediction = res.data
            this.setState({
                student:{
                    std_name: prediction.std_name,
                    std_id: prediction.std_id,
                    std_room: prediction.std_room,
                    avatar: prediction.avatar === 'bk1.png' ? 'bk1.png':'data:image/jpeg;base64,' + prediction.avatar
                },
            })
            
        }).catch((error) => {
            console.log(error)
        });
    };
    componentWillUnmount() {
        clearInterval(this.interval);
      }
    onChange = (event) => {
        event.preventDefault();
        let link_created = event.target.files[0] ? URL.createObjectURL(event.target.files[0]) : ''
        clearInterval(this.interval);
        this.setState({
            image_link:link_created,
            imageCaptured: event.target.files[0],
            camHidden: link_created === '' ? false: true,
            imgHidden: link_created === '' ? true: false,
            btnDisable: link_created === '' ? true: false
        });
    }
    backToCamera = () => {
        this.setState({
            imgHidden: true,
            camHidden: false,
            btnDisable: true
        })
        this.interval = setInterval(this.intervalRecog, 3000);
    }
    intervalRecog = () => {
        const imageSrc = this.webcam.getScreenshot();
        const formData = new FormData();
        formData.append('image', imageSrc)
        if (!this.state.camHidden)
            Axios.post(
                'http://127.0.0.1:9999/attend',
                formData,
                { headers: { 'content-type': 'multipart/form-data' } }
            ).then((res) => {
                let prediction = res.data
                this.setState({
                    student:{
                        std_name: prediction.std_name,
                        std_id: prediction.std_id,
                        std_room: prediction.std_room,
                        avatar: prediction.avatar === 'bk1.png' ? 'bk1.png':'data:image/jpeg;base64,' + prediction.avatar
                    }
                })
        }).catch((error) => {
            console.log(error)
        });
    }

    componentDidMount() {
        this.interval = setInterval(this.intervalRecog, 3000);
    }


    render() {
        const videoConstraints = {
            width: 640,
            height: 480,
            facingMode: "user"
        };
        return (
            <Form className="segment centered" >
                <Header/>
                <Table>
                    <Table.Header>
                        <Table.HeaderCell style={{ textAlign: 'center', fontSize: '30px', backgroundColor: 'CornflowerBlue' }}>HỆ THỐNG ĐIỂM DANH</Table.HeaderCell>
                    </Table.Header>
                </Table>
                <Grid>
                    <Grid.Row stretched>
                        <Grid.Column width={8} className="noPadding">
                            <Webcam
                                mirrored={true}
                                audio={false}
                                ref={this.setRef}
                                screenshotFormat="image/jpeg"
                                videoConstraints={videoConstraints} hidden={this.state.camHidden} />
                            <Image src={this.state.image_link} hidden={this.state.imgHidden} size='large' centered/>
                        </Grid.Column>
                        <Grid.Column width={8}   >
                            <Image src={this.state.student.avatar} size='medium'centered/>
                            <Modal.Description style={{marginTop:'2.5em', marginLeft:'15em'}} >
                                <h4 >Họ và tên: {this.state.student.std_name}</h4>
                                <h4>MSSV: {this.state.student.std_id}</h4>
                                <h4>Phòng: {this.state.student.std_room}</h4>
                            </Modal.Description>
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row columns={2} textAlign='center'>
                        <Grid.Column width={8}  >
                            <Button as="label" htmlFor="file" type="button">Chọn hình ảnh</Button>
                                <input type="file" id="file" hidden onChange={this.onChange} />
                            <Button primary onClick={this.recog_image} disabled={this.state.btnDisable}>Nhận dạng ảnh</Button>
                        </Grid.Column>
                        <Grid.Column width={8} >
                            <Button primary onClick={this.backToCamera} disabled={this.state.btnDisable}>Quay lại camera</Button>
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
                <Footer />
            </Form>
        );
    }

}


export default Home;