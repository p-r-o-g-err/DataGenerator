import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/actions';
import { Button, Table, Form, Row, Col } from 'react-bootstrap';
import { FaRegFileAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const apiUrl = process.env.REACT_APP_API_URL;

const Generator = () => {
    const { id } = useParams();
    const [generator, setGenerator] = useState(null);
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const intervalId = useRef(null);

    useEffect(() => {
        getGenerator();

        intervalId.current = setInterval(() => {
            getGenerator();
        }, 5000); 
    
        return () => clearInterval(intervalId.current); // очищаем интервал при размонтировании компонента
    }, [id]);

    const getGenerator = () => {
        fetch(`${apiUrl}/generator/${id}`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            setGenerator(data);
            console.log('generator', data);
            if (data.model_training_status.is_model_trained) {
                clearInterval(intervalId.current);
            }
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка получения генератора', 'error'));
        });
    };

    const startGenerationData = () => {
        navigate(`/generators/${generator.generator_id}/data-generation`);
    };

    return (
        generator && Object.keys(generator.model_config).length > 0 &&
        <div className="container mt-4 mb-5">
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="homeTitle">Генератор "{generator.name}"</h2>
                <div>
                    <Button variant="primary" onClick={startGenerationData}>
                        <FaRegFileAlt /> Сгенерировать данные
                    </Button>
                </div>
            </div>
            <div className="mt-4">
                {generator.model_training_status.is_model_trained ? (
                    <div>
                        <h4>
                            {'Точность модели: ' + ((generator.model_training_status.column_shapes_score+
                            generator.model_training_status.column_pair_trends_score)/2*100).toFixed(2) + '%'}
                        </h4>
                        <hr />
                        <h6 style={{color: 'gray'}}>
                            {'Точность воспроизведения зависимостей между признаками: ' + 
                            (generator.model_training_status.column_pair_trends_score*100) + '%'}
                        </h6>
                        <h6 style={{color: 'gray'}}>
                            {'Точность воспроизведения распределения признаков: ' + 
                            (generator.model_training_status.column_shapes_score*100) + '%'}
                        </h6>
                    </div>
                    
                
                ) : null}
            </div>
            <div className="mt-4 p-3 border">
                <h4 className="mb-3">Статус обучения</h4>
                <Table bordered hover>
                    <thead>
                        <tr>
                            <th>Этап</th>
                            <th>Прогресс</th>
                            {/* <th>Продолжительность</th> */}
                        </tr>
                    </thead>
                    <tbody>
                        <tr >
                            <td>Извлечение обучающих данных</td>
                            <td>{generator.model_training_status.is_fetched_data ? '100%' : '0%'}</td>
                            {/* <td>-</td> */}
                        </tr>
                        <tr>
                            <td>Обучение модели</td>
                            <td>{generator.model_training_status.is_model_trained ? '100%' : '0%'}</td>
                            {/* <td>-</td> */}
                        </tr>
                    </tbody>
                </Table>
            </div>
        </div>
    );
};

export default Generator;