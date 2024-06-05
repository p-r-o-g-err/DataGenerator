import React, { useState, useEffect } from 'react';
import { Table, Button, Spinner } from 'react-bootstrap';
import { FaPlus, FaTrash } from 'react-icons/fa';
import { useSelector, useDispatch } from 'react-redux';
import CreateGeneratorModal from './CreateGeneratorModal';
import { showNotification, setGenerators } from '../store/actions';
import { useNavigate } from 'react-router-dom';

const apiUrl = process.env.REACT_APP_API_URL;

const Generators = () => {
    const [show, setShow] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    
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
        setIsSaving(true);
        // console.log('Данные для создания генератора', userData.userId, name, originalDataset);
        
        const data = new FormData();
        data.append('originalDataset', originalDataset);
        data.append('userId', userData.userId);
        data.append('name', name);
        fetch(`${apiUrl}/generator/new`, {
            method: 'POST',
            body: data
        })
        .then(response => {
            if (!response.ok) 
                throw response;
            return response.json();
        })
        .then(data => {
            dispatch(showNotification('Генератор успешно создан', 'success'));
            getGenerators();
            // dispatch(setGenerator(data));
            // const generator = data;
            // console.log('Ответ от сервера', generator);
        })
        .catch((error) => {
            if (error.status === 413)
                dispatch(showNotification('Ошибка создания генератора. Файл должен содержать не менее 50 строк и 2 столбцов', 'error'));
            else
                dispatch(showNotification('Ошибка создания генератора', 'error'));
        })
        .finally(() => {
            setIsSaving(false);
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

    const handleGeneratorClick = (generator) => {
        if (generator.model_training_status.is_model_trained)
            navigate(`/generators/${generator.generator_id}`)
        else
            navigate(`/generators/${generator.generator_id}/data-config`)
    }

    if (isSaving) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <Spinner animation="border" role="status" />
                <span style={{marginLeft: '5px'}}>Создание генератора...</span>
            </div>
        );
    }

    return (
        <div className="container mt-4 mb-5">
            <CreateGeneratorModal handleClose={handleClose} show={show} createGenerator={createGenerator}/>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="myTitle">Генераторы</h2>
                <Button variant="primary" onClick={handleShow}>
                    <FaPlus /> Создать генератор
                </Button>
            </div>
            {generators && generators.length > 0 ? (
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
                                onClick={()=>handleGeneratorClick(generator)}
                            >
                                <td>{generator.name}</td>
                                <td>{generator.model_training_status.is_model_trained ? 'Готовый' : 'Новый'}</td>
                                <td style={{display: 'flex', justifyContent: 'space-between'}}>
                                    {new Date(generator.created_at).toLocaleString()}
                                    <FaTrash 
                                        className="trashIcon"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            deleteGenerator(generator.generator_id);
                                        }} 
                                    />
                                </td> 
                            </tr>
                        ))}
                    </tbody>
                </Table>
            ) : (
                <p style={{ 
                    color: 'gray', 
                    fontSize: '20px', 
                    textAlign: 'center',
                    marginTop: '50px'
                }}>
                    Генераторов не найдено
                </p>
            )}
        </div>
    );
};

export default Generators;