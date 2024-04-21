import React, { } from 'react';
import { Table, Button } from 'react-bootstrap';
import { FaPlus } from 'react-icons/fa';

const Generators = () => {
    return (
        <div className="container mt-5 mb-5">
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h2 className="homeTitle">Генераторы</h2>
                <Button variant="primary">
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