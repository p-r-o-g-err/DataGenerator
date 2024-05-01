import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/actions';
import { Table, Button, Form } from 'react-bootstrap';
import { FaCog, FaSave } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const apiUrl = process.env.REACT_APP_API_URL;

const DataConfig = () => {
    const { id } = useParams();
    const [generator, setGenerator] = useState(null);
    const dispatch = useDispatch();
    const navigate = useNavigate();

    useEffect(() => {
        getGenerator();
    }, [id]);

    const getGenerator = () => {
        fetch(`${apiUrl}/generator/${id}`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            setGenerator(data);
            // console.log('dataset_metadata', data.dataset_metadata);
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка получения генератора', 'error'));
        });
    }

    const dataTypeTranslations = {
        "numerical digital": "числовой дискретный",
        "numerical continuous": "числовой непрерывный",
        "categorical": "категориальный",
        "datetime": "дата и время",
        "boolean": "логический"
    };

    const handleDataTypeChange = (index, newDataType) => {
        const newGenerator = {...generator};
        newGenerator.dataset_metadata[index].sdtype = newDataType;
        setGenerator(newGenerator);
    }

    const handleSaveChanges = () => {
        fetch(`${apiUrl}/generator/update/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(generator)
        })
        .then(() => {
            dispatch(showNotification('Изменения сохранены', 'success'));
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка сохранения изменений', 'error'));
        });
    }

    return (
        generator &&
        <div className="container mt-4 mb-5">
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="homeTitle">Генератор "{generator.name}" - настройка данных</h2>
                <div>
                    
                    <Button style={{marginRight: '5px'}} variant="success" onClick={handleSaveChanges}>
                        <FaSave /> Сохранить изменения 
                    </Button>
                    <Button variant="primary" onClick={()=> navigate(`/generators/${generator.generator_id}/model-config`)}>
                        <FaCog /> Настроить модель 
                    </Button>
                </div>
            </div>
            <Table bordered hover>
                <thead>
                    <tr>
                        <th>Название столбца</th>
                        <th>Тип данных</th>
                    </tr>
                </thead>
                <tbody>
                    {generator.dataset_metadata.map((column, index) => (
                        <tr key={index}>
                            <td>{column.name}</td>
                            <td>
                                <Form.Select value={column.sdtype} onChange={(e) => handleDataTypeChange(index, e.target.value)}>
                                    {Object.keys(dataTypeTranslations).map(dataType => (
                                        <option key={dataType} value={dataType}>{dataTypeTranslations[dataType]}</option>
                                    ))}
                                </Form.Select>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </div>
    );
};

export default DataConfig;