import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/actions';
import { Button, Form, Row, Col } from 'react-bootstrap';
import { FaPlay, FaSave } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const apiUrl = process.env.REACT_APP_API_URL;


const ModelConfig = () => {
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
            // if (Object.keys(data.model_config).length === 0) {
            //     data.model_config = defaultModelConfig;
            // }
            setGenerator(data);
            // console.log('dataset_metadata', data.dataset_metadata);
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка получения генератора', 'error'));
        });
    }

    const handleModelConfigChange = (parameter, value) => {
        console.log('Изменение параметра', parameter, 'на', value);
        console.log('generator', generator);
        const newGenerator = {...generator};
        newGenerator.model_config[parameter] = isNaN(parseInt(value)) ? value : parseInt(value);
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

    const startTraining = () => {
        fetch(`${apiUrl}/generator/train/${id}`, {
            method: 'POST'
        })
        .then(() => {
            dispatch(showNotification('Обучение запущено', 'success'));
            navigate(`/generators/${generator.generator_id}`);
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка запуска обучения', 'error'));
        });
    }

    return (
        generator &&
        <div className="container mt-4 mb-5">
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="homeTitle">Генератор "{generator.name}" - настройка модели</h2>
                <div>
                    <Button style={{marginRight: '5px'}} variant="success" onClick={handleSaveChanges}>
                        <FaSave /> Сохранить изменения 
                    </Button>
                    <Button variant="primary" onClick={startTraining}>
                        <FaPlay /> Начать обучение
                    </Button>
                </div>
            </div>
            <Row className="g-3">
                <Col md>
                    <Form.Group controlId="modelSelect">
                        <Form.Label>Модель</Form.Label>
                        <Form.Select 
                            value={generator.model_config['model']}
                            onChange={(e) => handleModelConfigChange('model', e.target.value)}
                        >
                            <option>GaussianCopula</option>
                            <option>CTGAN</option>
                            <option>TVAE</option>
                        </Form.Select>
                    </Form.Group>
                </Col>
                {/* <Col md>
                    <Form.Group controlId="numVariants">
                        <Form.Label>Количество сгенерированных вариантов</Form.Label>
                        <Form.Control 
                            type="number" 
                            min="1" max="1000"
                            value={generator.model_config['num_variants']} 
                            onChange={(e) => handleModelConfigChange('num_variants', e.target.value)} 
                            onBlur={(e) => onBlurNumVariants(e)}
                        />
                    </Form.Group>
                </Col>
                <Col md>
                    <Form.Group controlId="numRecords">
                        <Form.Label>Количество записей в вариантах</Form.Label>
                        <Form.Control 
                            type="number" 
                            min="1" max="10000"
                            value={generator.model_config['num_records']} 
                            onChange={(e) => handleModelConfigChange('num_records', e.target.value)} 
                            onBlur={(e) => onBlurNumRecords(e)}
                        />
                    </Form.Group>
                </Col> */}
            </Row> 
        </div>
    );
};

export default ModelConfig;