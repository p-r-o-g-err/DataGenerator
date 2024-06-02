import React, { useEffect } from 'react';
import { useState } from 'react';
import { Button, Modal, Form, InputGroup } from 'react-bootstrap';
import Dropzone from 'react-dropzone';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/actions';

function CreateGeneratorModal({handleClose, show, createGenerator}) {
    const [originalDataset, setOriginalDataset] = useState(null);
    const [name, setName] = useState("")
    const dispatch = useDispatch();

    useEffect(() => {
        if (!show) {
            setOriginalDataset(null);
            setName("");
        }
    }, [show]);

    const handleDrop = (acceptedFiles) => {
        const fileNameByParts = acceptedFiles[0].name.split('.');
        const typeFile = fileNameByParts[fileNameByParts.length-1].toLowerCase();
        const nameFile = fileNameByParts[fileNameByParts.length-2];
        if (typeFile !== 'csv') {
            dispatch(showNotification('Поддерживаются файлы только в формате CSV', 'error'));
            return;
        }
        
        const MAX_FILE_SIZE = 10 * 1024 * 1024;
        if (acceptedFiles[0].size > MAX_FILE_SIZE) {
            dispatch(showNotification(`Файл слишком большой! Максимальный размер файла: ${MAX_FILE_SIZE / (1024 * 1024)} MБ`, 'error'));
            return;
        }
        
        // console.log('data', data);
        setOriginalDataset(acceptedFiles[0]);
        setName(nameFile);
    }

    const handleContinue = () => {
        if (!originalDataset) {
            dispatch(showNotification('Загрузите файл', 'error'));
            return;
        }
        if (name === '') {
            dispatch(showNotification('Введите название генератора', 'error'));
            return;
        }
        if (name.length > 100) {
            dispatch(showNotification('Название генератора не должно превышать 100 символов', 'error'));
            return;
        }
        if (!/^[a-zA-Zа-яА-Я0-9 -_]+$/.test(name)) {
            dispatch(showNotification('Название генератора должно содержать только буквы, цифры, пробелы, тире, нижнее подчеркивание и не начинаться с пробела', 'error'));
            return;
        }
        createGenerator(name.trim(), originalDataset);
        handleClose();
    }

    return (
        <div>
            <Modal
                show={show}
                onHide={handleClose}
                backdrop="static"
                keyboard={false}
                centered
            >
                <Modal.Header closeButton>
                    <Modal.Title>Загрузка данных</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Dropzone 
                        onDrop={acceptedFiles => handleDrop(acceptedFiles)} 
                        multiple={false} 
                        disabled={originalDataset !== null}
                    >
                        {({getRootProps, getInputProps}) => (
                            <section >
                                <div {...getRootProps()} style={{textAlign: 'center'}} 
                                    className={`${!originalDataset ? 'uploadingDataDivEnabled' : 'uploadingDataDivDisabled'}`}
                                >
                                    <input {...getInputProps()} accept=".csv"/>
                                    { originalDataset ?
                                        <p className='mb-0'>Загружен файл {originalDataset.name}</p> :
                                        <div className='mb-0'>
                                            <p>Перетащите файл сюда или кликните для выбора файла</p>
                                            <p>Поддерживаются файлы в формате CSV размером не более 10 МБ</p>
                                        </div>
                                    }
                                </div>
                            </section>
                        )}
                    </Dropzone>
                    {originalDataset && 
                        <InputGroup className="mt-3">
                            <InputGroup.Text id="inputGroup-sizing-default">
                                Название генератора
                            </InputGroup.Text>
                            <Form.Control
                                aria-label="Default"
                                aria-describedby="inputGroup-sizing-default"
                                value={name} onChange={e => setName(e.target.value)}
                            />
                        </InputGroup>
                    }
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={handleClose}>
                        Отмена
                    </Button>
                    <Button variant="primary" onClick={handleContinue}>
                        Продолжить
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    ); 
}

export default CreateGeneratorModal;