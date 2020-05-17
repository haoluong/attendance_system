import React, { Component } from 'react';
import Webcam from "react-webcam";
import Header from "../../components/Header/header";
import Footer from "../../components/Footer/footer"
import { Form, Modal, Button, Image, Input, Grid, Table } from 'semantic-ui-react'
import Axios from 'axios';

function buildFileSelector() {
    const fileSelector = document.createElement('input');
    fileSelector.setAttribute('type', 'file');
    fileSelector.setAttribute('multiple', 'multiple');
    // fileSelector.setAttribute('value', source);
    return fileSelector;
}

class Home extends Component {
    constructor(props) {
        super(props);
        this.state = {
            student: {
                std_name: '',
                std_id: '',
                std_room: ''
            },
            imageCaptured: '',
            camHidden: false,
            imgHidden: true, 
            source: ''
        }
    }
    setRef = webcam => {
        console.log(webcam)
        this.webcam = webcam;
    };

    capture = () => {
        const imageSrc = this.webcam.getScreenshot();
        const formData = new FormData();
        this.setState({
            imageCaptured: imageSrc,
            camHidden: true,
            imgHidden: false
        })
        formData.append('image', imageSrc)
        Axios.post(
            'http://127.0.0.1:9999/home',
            formData,
            { headers: { 'content-type': 'multipart/form-data' } }
        ).then((res) => {
        }).catch((error) => {
            console.log(error)
        });
    };
    handleFileSelect = (event) => {
        event.preventDefault();
        this.fileSelector.click();
        // let link_created = event.target.files[0] ? URL.createObjectURL(event.target.files[0]) : ''
        // this.setState({
        //   image:event.target.files[0],
        // });
    }


    componentDidMount() {
        this.fileSelector = buildFileSelector();
        this.interval = setInterval(() => {
            const imageSrc = this.webcam.getScreenshot();
            const formData = new FormData();
            formData.append('image', imageSrc)
            Axios.post(
                'http://127.0.0.1:9999/attend',
                formData,
                { headers: { 'content-type': 'multipart/form-data' } }
            ).then((res) => {
                console.log(res)
            }).catch((error) => {
                console.log(error)
            });
        }, 1000);
    }


    render() {
        const videoConstraints = {
            width: 1280,
            height: 720,
            facingMode: "user"
        };
        return (
            <Form className="segment centered" >
                <Header />
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
                            <Image src={this.state.imageCaptured} hidden={this.state.imgHidden}/>
                        </Grid.Column>
                        <Grid.Column width={4} className="noPadding">
                            <Image src='bk1.png' wrapped />
                        </Grid.Column>
                        <Grid.Column width={4} className="noPadding">
                            <Modal.Description>
                                <h4 >Họ và tên:</h4>
                                <h4>MSSV:</h4>
                                <h4>Phòng: </h4>
                            </Modal.Description>
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row centered columns={3}>
                        <Grid.Column width={10}>
                            <Button primary onClick={this.capture}>Chụp</Button>
                            <Button primary onClick={this.handleFileSelect}>Tải ảnh</Button>
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
                <Footer />
            </Form>
        );
    }

}


export default Home;