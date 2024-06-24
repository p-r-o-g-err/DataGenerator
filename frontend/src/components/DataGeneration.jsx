import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/actions';
import { Button, Table, Form, Row, Col, Spinner } from 'react-bootstrap';
import { FaRegFileAlt } from 'react-icons/fa';

const apiUrl = process.env.REACT_APP_API_URL;

const DataGeneration = () => {
    const { id } = useParams();
    const [generator, setGenerator] = useState(null);
    const [numVariants, setNumVariants] = useState(1);
    const [numRecords, setNumRecords] = useState(1000);
    const [addReport, setAddReport] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);
    const dispatch = useDispatch();

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
            console.log('generator', data);
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка получения генератора', 'error'));
        });
    };


    const onBlurNumVariants = (e) => {
        const value = e.target.value;
        if (value < 1) {
            handleNumVariantsChange(1);
        } else if (value > 1000) {
            handleNumVariantsChange(1000);
        } else if (!Number.isInteger(Number(value))) {
            handleNumVariantsChange(Math.floor(value));
        }
    }

    const onBlurNumRecords = (e) => {
        const value = e.target.value;
        if (value < 1) {
            handleNumRecordsChange(1);
        } else if (value > 10000) {
            handleNumRecordsChange(10000);
        } else if (!Number.isInteger(Number(value))) {
            handleNumRecordsChange(Math.floor(value));
        }
    }

    const handleNumVariantsChange = (value) => {
        setNumVariants(parseInt(value));
    }

    const handleNumRecordsChange = (value) => {
        setNumRecords(parseInt(value));
    }

    const startGenerationData = () => {
        setIsGenerating(true);
        fetch(`${apiUrl}/generator/generate/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                num_variants: numVariants,
                num_records: numRecords,
                add_report: addReport
            })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob); // Создаем URL для blob
            const a = document.createElement('a'); // Создаем элемент 'a'
            a.style.display = 'none';
            a.href = url;
            a.download = `${generator.name}_synthetic_data.zip`; // Имя файла для скачивания
            document.body.appendChild(a); // Добавляем 'a' на страницу
            a.click();
            document.body.removeChild(a); // Удаляем 'a' после скачивания
            dispatch(showNotification('Данные успешно сгенерированы', 'success'));
            // dispatch(showNotification('Запущена генерация данных', 'success'));
        })
        .catch((error) => {
            dispatch(showNotification('Ошибка генерации данных', 'error'));
        })
        .finally(() => {
            setIsGenerating(false);
        });
    };

    if (isGenerating) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <Spinner animation="border" role="status" />
                <span style={{marginLeft: '5px'}}>Генерация данных...</span>
            </div>
        );
    }

    return (
        generator && Object.keys(generator.model_config).length > 0 &&
        <div className="container mt-4 mb-5">
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="myTitle">Генератор "{generator.name}" - Настройка генерации</h2>
                <div>
                    <Button variant="primary" onClick={startGenerationData}>
                        <FaRegFileAlt /> Сгенерировать данные
                    </Button>
                </div>
            </div>
            <Row className="g-3 justify-content-center">
                <Col md={3}>
                    <Form.Group controlId="numVariants">
                        <Form.Label>Количество сгенерированных вариантов</Form.Label>
                        <Form.Control 
                            type="number" 
                            min="1" max="1000"
                            value={numVariants} 
                            onChange={(e) => handleNumVariantsChange(e.target.value)} 
                            onBlur={(e) => onBlurNumVariants(e)}
                        />
                    </Form.Group>
                </Col>
                <Col md={3}>
                    <Form.Group controlId="numRecords">
                        <Form.Label>Количество записей в вариантах</Form.Label>
                        <Form.Control 
                            type="number" 
                            min="1" max="10000"
                            value={numRecords} 
                            onChange={(e) => handleNumRecordsChange(e.target.value)} 
                            onBlur={(e) => onBlurNumRecords(e)}
                        />
                    </Form.Group>
                </Col>
                <Col md={3}>
                    <Form.Group controlId="addReport">
                        <Form.Check 
                            type="switch"
                            label="Сформировать отчет"
                            checked={addReport}
                            onChange={(e) => setAddReport(e.target.checked)}
                        />
                        <Form.Text className="text-muted">
                            Потребуется больше времени
                        </Form.Text>
                    </Form.Group>
                </Col>
            </Row> 
        </div>
    );
};

export default DataGeneration;