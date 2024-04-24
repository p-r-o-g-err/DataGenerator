import React, { useState, useEffect } from 'react';
import { Table, Button } from 'react-bootstrap';
import { FaPlus, FaTrash } from 'react-icons/fa';
import { useSelector, useDispatch } from 'react-redux';
import CreateGeneratorModal from './CreateGeneratorModal';
import { showNotification, setGenerators } from '../store/actions';
import { useNavigate } from 'react-router-dom';

const apiUrl = process.env.REACT_APP_API_URL;

const Generators = () => {
    const [show, setShow] = useState(false);
    const userData = useSelector(state => state.userData);
    const generators = useSelector(state => state.generators);

    const dispatch = useDispatch();
    const navigate = useNavigate();
    
    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    useEffect(() => {
        getGenerators();
    }, []);

    const getGenerators = () => {
        fetch(`${apiUrl}/generator/all`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            dispatch(setGenerators(data));
            console.log('Генераторы', data);
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка получения генераторов', 'error'));
        });
    };

    const createGenerator = (name, originalDataset) => {
        console.log('Данные для создания генератора', userData.userId, name, originalDataset);
        
        const data = new FormData();
        data.append('originalDataset', originalDataset);
        data.append('userId', userData.userId);
        data.append('name', name);
        fetch(`${apiUrl}/generator/new`, {
            method: 'POST',
            body: data
        })
        .then(response => response.json())
        .then(data => {
            dispatch(showNotification('Генератор успешно создан', 'success'));
            getGenerators();
            // dispatch(setGenerator(data));
            // const generator = data;
            // console.log('Ответ от сервера', generator);
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка создания генератора', 'error'));
        });
    }

    const deleteGenerator = (id) => {
        console.log('Удаление генератора с ID', id);
        fetch(`${apiUrl}/generator/delete/${id}`, {
            method: 'DELETE'
        })
        .then(() => {
            dispatch(showNotification('Генератор успешно удален', 'success'));
            getGenerators();
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка удаления генератора', 'error'));
        });
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
                    {generators && [...generators].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).map(generator => (
                        <tr 
                            key={generator.generator_id}
                            className="generatorRow"
                            onClick={()=> navigate(`/generators/${generator.generator_id}/data-config`)}
                        >
                            <td>{generator.name}</td>
                            <td>{Object.keys(generator.model_config).length === 0 ? 'Новый' : 'Готовый'}</td>
                            <td style={{display: 'flex', justifyContent: 'space-between'}}>
                                {new Date(generator.created_at).toLocaleString()}
                                <FaTrash 
                                    className="trashIcon"
                                    onClick={() => deleteGenerator(generator.generator_id)} 
                                />
                            </td> 
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    );
};

export default Generators;