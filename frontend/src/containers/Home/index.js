import React, {Component} from 'react';
import Header from "../../components/Header/header";
import Footer from "../../components/Footer/footer"
import {Image, Divider} from 'semantic-ui-react'

class Home extends Component {
    constructor(props) {
        super(props);
        this.state = {
            trending_list: [],
            best_seller_list: [],
        }
    }

    // componentDidMount() {
    //       HttpUtils.getJson('/products?limit=8')
    //       .then(data => {
    //             this.setState({
    //                 trending_list: data.data,
    //                 best_seller_list: data.data
    //             })
                
    //       })
    //       .catch(err => {

    //       })
    //   }


    render() {
        return(
            <div>
                <Header />
                <Divider hidden />
    <Image.Group size='large'>
                <Image src="/bk1.png"/>
                <Image src="/bk2.png"/>
                <Image src="/bk3.png"/>
                </Image.Group>
                <Footer/>
            </div>
        );
    }

}


export default Home;