import React, { useState } from 'react';
import { Table, Button } from 'react-bootstrap';
import { FaPlus } from 'react-icons/fa';
import { useSelector } from 'react-redux';
import CreateGeneratorModal from './CreateGeneratorModal';
import { showNotification } from '../store/actions';

const apiUrl = process.env.REACT_APP_API_URL;

const Generators = () => {
    const [show, setShow] = useState(false);
    const userData = useSelector(state => state.userData);

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    const createGenerator = (name, originalDataset) => {
        console.log('Данные для создания генератора', userData.userId, name, originalDataset);

        // const data = new FormData();
        // data.append('file', acceptedFiles[0]);

        // fetch(`${apiUrl}/get_data`, {
        //     method: 'POST',
        //     body: data,
        // })
        // .then(response => response.json())
        // .then(data => {
        //     console.log(data);
        // })
        // .catch((error) => {
        //     console.error('Error:', error);
        // });
    }

    return (
        <div className="container mt-4 mb-5">
            <CreateGeneratorModal handleClose={handleClose} show={show} createGenerator={createGenerator}/>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="homeTitle">Генераторы</h2>
                <Button variant="primary" onClick={handleShow}>
                    <FaPlus /> Создать генератор
                </Button>
            </div>
            <Table bordered hover>
                <thead>
                    <tr>
                        <th>Название</th>
                        <th>Статус</th>
                        <th>Дата создания</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Тест</td>
                        <td>Новый</td>
                        <td>1 минуту назад</td>
                    </tr>
                </tbody>
            </Table>
        </div>
    );
};

export default Generators;