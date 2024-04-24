// import logo from './logo.svg';
import './App.css';
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import { useDispatch, useSelector } from 'react-redux';
import { setUserData } from './store/actions';
import {Spinner} from 'react-bootstrap';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Notify from './components/Notify';


import Home from './components/Home';
import Generators from './components/Generators';
import DataConfig from './components/DataConfig';
import withAuthCheck from './components/withAuthCheck';

// Защита компонентов от неавторизованных пользователей
const ProtectedGenerators = withAuthCheck(Generators);
const ProtectedDataConfig = withAuthCheck(DataConfig);

const apiUrl = process.env.REACT_APP_API_URL;

function App() {
    const [isLoading, setIsLoading] = useState(true);
    const dispatch = useDispatch();
    const notification = useSelector(state => state.notification);
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth  = async () => {
        const accessToken = localStorage.getItem('yandexAccessToken');
        if (accessToken) {
            try {
                const response = await fetch(`${apiUrl}/auth/yandex`, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                const data = await response.json();
                if (response.ok) {
                    dispatch(setUserData({ userId: data.user_id, firstName: data.first_name, lastName: data.last_name }));
                } else {
                    localStorage.removeItem('yandexAccessToken');
                }
            } catch (error) {
                localStorage.removeItem('yandexAccessToken');
            }
        }
        setIsLoading(false);
    };
  
    if (isLoading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Загрузка...</span>
                </Spinner>
            </div>
        );
    }
    return (
        <BrowserRouter>
            {notification && <Notify message={notification.message} type={notification.type} />}
            <Header/> 
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/generators" element={<ProtectedGenerators />} />
                <Route path="/generators/:id/data-config" element={<ProtectedDataConfig />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
