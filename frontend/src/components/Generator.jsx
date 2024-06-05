import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/actions';
import { Button, Table, Form, Row, Col, Spinner } from 'react-bootstrap';
import { FaRegFileAlt, FaFileDownload  } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const apiUrl = process.env.REACT_APP_API_URL;

const Generator = () => {
    const { id } = useParams();
    const [generator, setGenerator] = useState(null);
    const [sampleData, setSampleData] = useState(null);
    const [columns, setColumns] = useState([]);
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
            if (data.model_training_status.is_report_generated) {
                clearInterval(intervalId.current);
                fetchSampleData();
            }
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка получения генератора', 'error'));
        });
    };

    const startGenerationData = () => {
        navigate(`/generators/${generator.generator_id}/data-generation`);
    };

    const downloadReport = () => {
        fetch(`${apiUrl}/generator/download-report/${id}`, {
            method: 'GET'
        })
        .then(response => {
            if (!response.ok) 
                throw response;
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob); // Создаем URL для blob
            const a = document.createElement('a'); // Создаем элемент 'a'
            a.style.display = 'none';
            a.href = url;
            a.download = `${generator.name}_report.html`; // Имя файла для скачивания
            document.body.appendChild(a); // Добавляем 'a' на страницу
            a.click();
            document.body.removeChild(a); // Удаляем 'a' после скачивания
        })
        .catch((error) => {
            // console.log('error', error)
            if (error.status === 404)
                dispatch(showNotification('Отчет не найден', 'error'));
            else
                dispatch(showNotification('Ошибка получения отчета', 'error'));
        });
    };

    const fetchSampleData = () => {
        fetch(`${apiUrl}/generator/sample-data/${id}`, {
            method: 'GET',
            headers: {
                'content-type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) 
                throw response;
            return response.json();
        })
        .then(data => {
            setSampleData(data[0]);
            setColumns(data[1]);
            console.log('sample_data', data);
        })
        .catch((error) => {
            dispatch(showNotification('Пример сгенерированных данных не найден', 'error'));
        });
    }

    return (
        generator && Object.keys(generator.model_config).length > 0 &&
        <div className="container mt-4 mb-5">
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="homeTitle">Генератор "{generator.name}"</h2>
                <div>
                    <Button variant="info" style={{marginRight: '5px'}}  disabled={!generator.model_training_status.is_report_generated} onClick={downloadReport}>
                        <FaFileDownload /> Скачать отчет
                    </Button>
                    <Button variant="primary" disabled={!generator.model_training_status.is_report_generated} onClick={startGenerationData}>
                        <FaRegFileAlt /> Сгенерировать данные
                    </Button>
                </div>
            </div>
            <div className="mt-4">
                {generator.model_training_status.is_report_generated ? (
                    <div>
                        <h4>
                            {'Точность модели: ' + ((generator.model_training_status.column_shapes_score+
                            generator.model_training_status.column_pair_trends_score)/2*100).toFixed(2) + '%'}
                        </h4>
                        <hr />
                        <h6 style={{color: 'gray'}}>
                            {'Точность воспроизведения зависимостей между признаками: ' + 
                            (generator.model_training_status.column_pair_trends_score*100).toFixed(2) + '%'}
                        </h6>
                        <h6 style={{color: 'gray'}}>
                            {'Точность воспроизведения распределения признаков: ' + 
                            (generator.model_training_status.column_shapes_score*100).toFixed(2) + '%'}
                        </h6>
                    </div>
                ) : null}
            </div>
            {generator.model_training_status.is_report_generated && sampleData ? (
                <div className="mt-4 p-3 border">
                    <h4 className="mb-3">Пример сгенерированных данных</h4>
                    <div  style={{ overflowX: 'auto' }}>
                    <Table striped bordered hover size="sm">
                        <thead>
                            <tr>
                                {sampleData.length > 0 && columns.map(column => (
                                    <th key={column.column_number}>{column.name}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {sampleData.map((row, index) => (
                                <tr key={index}>
                                    {columns.map(column => (
                                    <td key={column.column_number}>{row[column.name]}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                    </div>
                </div>
            ) : null}
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
                            <td>{generator.model_training_status.is_fetched_data ? '100%' : 
                                <Spinner animation="border" role="status">
                                    <span className="visually-hidden">Загрузка...</span>
                                </Spinner>
                            }</td>
                        </tr>
                        <tr>
                            <td>Обучение модели</td>
                            <td>{generator.model_training_status.is_model_trained ? '100%' : 
                                <Spinner animation="border" role="status">
                                    <span className="visually-hidden">Загрузка...</span>
                                </Spinner>
                            }</td>
                        </tr>
                        <tr>
                            <td>Оценка точности</td>
                            <td>{generator.model_training_status.is_report_generated ? '100%' : 
                                <Spinner animation="border" role="status">
                                    <span className="visually-hidden">Загрузка...</span>
                                </Spinner>
                            }</td>
                        </tr>
                    </tbody>
                </Table>
            </div>
        </div>
    );
};

export default Generator;