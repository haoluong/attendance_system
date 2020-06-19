import React, { Component } from 'react';
import Header from "../../components/Header/header";
import { Table, Form, Pagination, Search, Grid, Menu, Modal, Image, Dropdown, Icon, Input, Button } from 'semantic-ui-react';
import Axios from 'axios';
import _ from 'lodash'
import faker from 'faker'
const initialState = { isLoading: false, results: [], value: '' }

const source = _.times(5, () => ({
    title: faker.company.companyName()
}))

const numofRow = [
    { key: 1, value: 1, text: '1' },
    { key: 2, value: 2, text: '2' },
    { key: 10, value: 10, text: '10' },
    { key: 20, value: 20, text: '20' },
    { key: 50, value: 50, text: '50' },
    { key: 100, value: 100, text: '100' }
]

class StudentList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            searchList: [],
            student: [],
            isLoading: false,
            results: [],
            value: {
                std_name: '',
                std_id: '',
                std_room: '',
            },
            box: '',
            openModal: false,
            selectedStudent: {
                avatar: 'https://react.semantic-ui.com/images/avatar/large/rachel.png',
                std_name: '',
                std_id: '',
                std_room: '',
            },
            column: null,
            direction: null,
            page: 1,
            number_of_rows: 10,
            total_record: 10,
            modal: {
                std_id: null,
                history: [],
                total: 0,
                page: 1,
                number_of_rows: 5
            },
            enableInput: true,
            btnHidden: true,
            tempName: '',
            tempId: '',
            tempRoom: ''
        }
    }

    handleResultSelect = (event, { result, box }) => {
        event.preventDefault();
        let value_clone = this.state.value
        value_clone[box] = result.title
        this.setState({
            isLoading: true,
            value: value_clone, box
        })
        let url = "http://127.0.0.1:9999/studentlist?std_name=" + value_clone.std_name
            + "&std_id=" + value_clone.std_id + "&std_room=" + value_clone.std_room
            + "&page=" + this.state.page + "&number_of_rows=" + this.state.number_of_rows
        Axios.get(url)
            .then((res) => {
                const student = res.data.data;
                const total_record = res.data.total;
                this.setState({ isLoading: false, student, total_record });
            }).catch((error) => {
                console.log(error)
            });
    }

    handleSearchChange = (e, { value, box }) => {
        let value_clone = this.state.value
        value_clone[box] = value
        if (value === "") {
            window.location.reload();
        }
        this.setState({
            isLoading: true,
            value: value_clone, box
        })
        let url = "http://127.0.0.1:9999/studentlist?std_name=" + value_clone.std_name
            + "&std_id=" + value_clone.std_id + "&std_room=" + value_clone.std_room
        Axios.get(url)
            .then((res) => {
                const searchList = res.data.data;
                this.setState({ isLoading: false, searchList });
            }).catch((error) => {
                console.log(error)
            });
        setTimeout(() => {
            if (this.state.value.length < 1) return this.setState(initialState)

            const re = new RegExp(_.escapeRegExp(this.state.value[box]), 'i')
            const isMatch = (result) => re.test(result.title)
            let clone_student = this.state.searchList.map(ele => {
                return {
                    title: ele[this.state.box]
                }
            })
            this.setState({
                isLoading: false,
                results: _.filter(clone_student, isMatch),
            })
        }, 300)
    }

    query_history = (obj) => {
        const { std_id, page, number_of_rows } = obj
        let url = "http://127.0.0.1:9999/stdhistory?std_id=" + std_id
            + "&page=" + page + "&number_of_rows=" + number_of_rows
        Axios.get(url)
            .then((res) => {
                const modal = {
                    std_id: std_id,
                    history: res.data.data,
                    total_record: res.data.total,
                    page: page,
                    number_of_rows: number_of_rows
                }
                this.setState({ modal });
            }).catch((error) => {
                console.log(error)
            });
    }

    onHistoryPageChange = (event, data) => {
        const modal = this.state.modal
        modal.page = data.activePage
        this.query_history(modal)
    }

    clickRow = (student) => {
        let url = "http://127.0.0.1:9999/avatar?std_id=" + student.std_id
        Axios.get(url, { responseType: 'arraybuffer' })
            .then((res) => {
                let base64Flag = 'data:image/jpeg;base64,';
                let student_clone = student
                if (res.data.byteLength > 100) {
                    student_clone.avatar = base64Flag + this.arrayBufferToBase64(res.data)
                } else {
                    student_clone.avatar = 'https://react.semantic-ui.com/images/avatar/large/rachel.png'
                }
                // console.log(student_clone.avatar)
                this.setState({
                    openModal: true,
                    selectedStudent: student_clone,
                    tempName: student_clone.std_name,
                    tempId: student_clone.std_id,
                    tempRoom: student_clone.std_room
                })
            }).catch((error) => {
                console.log("get avatar fail " + error)
            });
        let obj = this.state.modal
        obj.std_id = student.std_id
        this.query_history(obj)
    }
    arrayBufferToBase64(buffer) {
        var binary = '';
        var bytes = [].slice.call(new Uint8Array(buffer));
        bytes.forEach((b) => binary += String.fromCharCode(b));
        return window.btoa(binary);
    };
    closeModal = () => {
        this.setState({
            openModal: false,
            modal: {
                std_id: null,
                history: [],
                total: 0,
                page: 1,
                number_of_rows: 5
            }
        })
    }

    handleSort = (clickedColumn) => () => {
        const state_clone = this.state
        if (state_clone.column !== clickedColumn) {
            state_clone.column = clickedColumn
            state_clone.direction = 'ascending'
        } else if (state_clone.direction === 'ascending') {
            state_clone.direction = 'descending'
        } else if (state_clone.direction === 'descending') {
            state_clone.direction = null
        } else {
            state_clone.direction = 'ascending'
        }
        this.query_student(state_clone)
    }

    onPageChange = (event, data) => {
        const state_clone = this.state
        state_clone.page = data.activePage
        this.query_student(state_clone)
    }

    query_student = (obj) => {
        const { value, column, direction, page, number_of_rows } = obj
        let url = "http://127.0.0.1:9999/studentlist?std_name=" + value.std_name
            + "&std_id=" + value.std_id + "&std_room=" + value.std_room
            + "&page=" + page + "&number_of_rows=" + number_of_rows
        if (direction) {
            url += "&sort=" + column + "&direction=" + direction
        }
        Axios.get(url)
            .then((res) => {
                const student = res.data.data;
                const total_record = res.data.total
                this.setState({ student, value, column, direction, page, number_of_rows, total_record });
            }).catch((error) => {
                console.log(error)
            });
    }

    onResultSelect = (event, data) => {
        const state_clone = this.state
        state_clone.number_of_rows = data.value
        state_clone.page = 1
        this.query_student(state_clone)
    }

    btnUpdate = (event) => {
        this.setState({ enableInput: false, btnHidden: false });
    }

    editName = (event) => {
        let input_value = event.target.value
        if (input_value !== "" && input_value !== this.state.tempName) {
            this.setState({
                tempName: input_value
            });
        }
    }
    editId = (event) => {
        let input_value = event.target.value
        if (input_value !== "" && input_value !== this.state.tempId) {
            this.setState({
                tempId: input_value
            });
        }
    }
    editRoom = (event) => {
        let input_value = event.target.value
        if (input_value !== "" && input_value !== this.state.tempRoom) {
            this.setState({
                tempRoom: input_value
            });
        }
    }
    btnOK = (event) => {
        event.preventDefault();

        const tempStudent = {
            newName: this.state.tempName,
            newId: this.state.tempId,
            newRoom: this.state.tempRoom
        };
        // Axios.post('http://127.0.0.1:9999/update_student', tempStudent)
        //     .then((res) => {
        //         if (res.data["success"]) {
        //             History.push('/')
        //         }
        //         else {
        //             console.log(false)
        //         }
        //     }).catch((error) => {
        //         console.log(error)
        //     });
    }

    btnCancel = (event) => {
        this.setState({
            tempName: this.state.selectedStudent.std_name,
            tempId: this.state.selectedStudent.std_id,
            tempRoom: this.state.selectedStudent.std_room,
            enableInput: true,
            btnHidden: true
        })
    }

    componentDidMount() {
        this.query_student(this.state)
    }

    render() {
        const { isLoading, value, results, column, direction } = this.state
        return (
            <Form className="segment centered" >
                <Modal open={this.state.openModal} onClose={this.closeModal} className="segment centered">
                    <Modal.Header>Lịch sử hoạt động
                    <Button icon='edit' onClick={this.btnUpdate} floated='right'></Button>
                    </Modal.Header>
                    <Modal.Content image>
                        <Image width="260" height="260" wrapped src={this.state.selectedStudent.avatar} />
                        <Modal.Description>
                            <h4 >Họ và tên:</h4><Input disabled={this.state.enableInput} value={this.state.tempName} type="text" onChange={this.editName} />
                            <h4>MSSV:</h4><Input disabled={this.state.enableInput} value={this.state.tempId} type='text' onChange={this.editId} />
                            <h4>Phòng: </h4><Input disabled={this.state.enableInput} value={this.state.tempRoom} type="text" onChange={this.editRoom}/>
                            <Button.Group floated='right' >
                                <Button color='blue' inverted basic={this.state.btnHidden} floated='right'><Icon name='checkmark' onClick={this.btnOK} /> Yes</Button>
                                <Button color='red' inverted basic={this.state.btnHidden} floated='right' onClick={this.btnCancel}><Icon name='remove'  /> No</Button>
                            </Button.Group>
                        </Modal.Description>
                    </Modal.Content>
                    <Table celled>
                        <Table.Header>
                            <Table.Row>
                                <Table.HeaderCell>Trạng thái</Table.HeaderCell>
                                <Table.HeaderCell>Thời gian</Table.HeaderCell>
                            </Table.Row>
                        </Table.Header>

                        <Table.Body>
                            {this.state.modal.history.map(record =>
                                <Table.Row>
                                    <Table.Cell>{record.inKTX ? "Trong KTX" : "Ngoài KTX"}</Table.Cell>
                                    <Table.Cell>{record.detected_at}</Table.Cell>
                                </Table.Row>)}
                        </Table.Body>

                        <Table.Footer>
                            <Table.Row>
                                <Table.HeaderCell colSpan='5'>
                                    <Menu floated='right' pagination>
                                        <Pagination
                                            boundaryRange={0}
                                            activePage={this.state.modal.page}
                                            ellipsisItem={null}
                                            firstItem={null}
                                            lastItem={null}
                                            siblingRange={1}
                                            totalPages={Math.ceil(this.state.modal.total_record / this.state.modal.number_of_rows)}
                                            onPageChange={this.onHistoryPageChange} />
                                    </Menu>
                                </Table.HeaderCell>
                            </Table.Row>
                        </Table.Footer>

                    </Table>
                </Modal>
                <Header />
                <Grid columns="equal" textAlign='center' >
                    <Grid.Column>
                        <Search
                            placeholder="Họ và tên"
                            loading={isLoading}
                            onResultSelect={this.handleResultSelect}
                            onSearchChange={_.debounce(this.handleSearchChange, 500, {
                                leading: true,
                            })}
                            onKeyPress={(e) => { e.key === 'Enter' && e.preventDefault(); }}
                            results={results}
                            value={value.std_name}
                            box={"std_name"}
                            {...this.props}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <Search
                            placeholder="MSSV"
                            loading={isLoading}
                            onResultSelect={this.handleResultSelect}
                            onSearchChange={_.debounce(this.handleSearchChange, 500, {
                                leading: true,
                            })}
                            onKeyPress={(e) => { e.key === 'Enter' && e.preventDefault(); }}
                            results={results}
                            value={value.std_id}
                            box={"std_id"}
                            {...this.props}
                        />
                    </Grid.Column>
                    <Grid.Column>
                        <Search
                            placeholder="Phòng"
                            loading={isLoading}
                            onResultSelect={this.handleResultSelect}
                            onSearchChange={_.debounce(this.handleSearchChange, 500, {
                                leading: true,
                            })}
                            onKeyPress={(e) => { e.key === 'Enter' && e.preventDefault(); }}
                            results={results}
                            value={value.std_room}
                            box={"std_room"}
                            {...this.props}
                        />
                    </Grid.Column>
                </Grid>
                <Table sortable celled >

                    <Table.Header>
                        <Table.HeaderCell colSpan={5} style={{ textAlign: 'center', fontSize: '30px', backgroundColor: 'CornflowerBlue' }}>BẢNG ĐIỂM DANH SINH VIÊN</Table.HeaderCell>
                        <Table.Row>
                            <Table.HeaderCell sorted={column === 'student.std_name' ? direction : null} onClick={this.handleSort("student.std_name")}>Họ và tên</Table.HeaderCell>
                            <Table.HeaderCell sorted={column === 'student.std_id' ? direction : null} onClick={this.handleSort("student.std_id")}>MSSV</Table.HeaderCell>
                            <Table.HeaderCell sorted={column === 'student.std_room' ? direction : null} onClick={this.handleSort("student.std_room")}>Phòng</Table.HeaderCell>
                            <Table.HeaderCell sorted={column === 'inKTX' ? direction : null} onClick={this.handleSort("inKTX")}>Trạng thái</Table.HeaderCell>
                            <Table.HeaderCell sorted={column === 'detected_at' ? direction : null} onClick={this.handleSort("detected_at")}>Thời gian</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>

                    <Table.Body>
                        {this.state.student.map(student =>
                            <Table.Row onClick={() => this.clickRow(student)} key={student.std_id}>
                                <Table.Cell>{student.std_name}</Table.Cell>
                                <Table.Cell>{student.std_id}</Table.Cell>
                                <Table.Cell>{student.std_room}</Table.Cell>
                                <Table.Cell>{student.inKTX ? "Trong KTX" : "Ngoài KTX"}</Table.Cell>
                                <Table.Cell>{student.detected_at}</Table.Cell>
                            </Table.Row>)}
                    </Table.Body>

                    <Table.Footer>
                        <Table.Row >
                            <Table.HeaderCell colSpan='5'>
                                <Dropdown options={numofRow} value={this.state.number_of_rows} selection closeOnChange={true} onChange={this.onResultSelect} />
                                <Menu floated='right' pagination>
                                    <Pagination
                                        boundaryRange={0}
                                        activePage={this.state.page}
                                        ellipsisItem={null}
                                        firstItem={null}
                                        lastItem={null}
                                        siblingRange={1}
                                        totalPages={Math.ceil(this.state.total_record / this.state.number_of_rows)}
                                        onPageChange={this.onPageChange} />
                                </Menu>
                            </Table.HeaderCell>
                        </Table.Row>
                    </Table.Footer>

                </Table>

            </Form>
        )
    };
}
export default StudentList
