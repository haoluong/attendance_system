import React, {Component} from 'react'
import { Redirect, Route, Router } from "react-router-dom"
import Home from './containers/Home/index'
import Login from './containers/Login/login'
import History from './components/History/history'
import StudentList from './containers/StudentList/index'
import NewStudent from './containers/NewStudent/index'
import MessageSuccess from './containers/Message/success'
import MessageError from './containers/Message/error'
class App extends Component {
  constructor(props) {
    super(props);
  }
  render() {
    return (
      <div>
        <Router history={History}>
          <Route exact path="/login" component={Login} />
          <Route exact path="/" component={Home} />
          <Route exact path="/studentlist" component={StudentList} />
          <Route exact path="/newstudent" component={NewStudent} />
          <Route exact path="/messagesuccess" component={MessageSuccess} />
          <Route exact path="/messageerror" component={MessageError} />
          {/* <Route path="" component={NotFound} /> */}
        </Router>
      </div>
    );
  }
}
export default App;
