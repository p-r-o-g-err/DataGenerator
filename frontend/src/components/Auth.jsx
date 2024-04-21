import React, { } from 'react';
import { YandexLogin, YandexLogout } from 'react-yandex-login';
import { useDispatch, useSelector } from 'react-redux';
import { setUserData, showNotification } from '../store/actions';
import { Button, NavDropdown, Nav } from 'react-bootstrap';
import yandexLogo from '../images/logo_yandex.png';
// import Notify from './Notify';
import './styles.css';

const clientID = process.env.REACT_APP_YANDEX_CLIENT_ID;
const apiUrl = process.env.REACT_APP_API_URL;

function Auth() {
    const dispatch = useDispatch();
    const userData = useSelector(state => state.userData);

    const loginSuccess = async (userData) => {
        let accessToken = userData.access_token;
        try {
            console.log('Вызов fetch');
            const response = await fetch(`${apiUrl}/auth/yandex`, {
                headers: {'Authorization': `Bearer ${accessToken}`}
            });
            const data = await response.json();
            console.log('Данные с сервера', data);

            if (response.ok) {
                localStorage.setItem('yandexAccessToken', accessToken);
                dispatch(setUserData({ firstName: data.first_name, lastName: data.last_name }));
                // dispatch(showNotification('Вы успешно авторизованы!', 'success'));
            } else {
                loginFailure();
            }
        } catch (error) {
            loginFailure();
        }
    }

    const loginFailure = () => {
        localStorage.removeItem('yandexAccessToken');
        dispatch(setUserData(null));
        dispatch(showNotification('Ошибка авторизации', 'error'));
    }
    
    const logoutSuccess = () => {
        localStorage.removeItem('yandexAccessToken');
        dispatch(setUserData(null));
    }

    return (
        <div>
            <Nav className="justify-content-center align-items-center">
                {!userData ?
                    <Nav.Link>
                        <YandexLogin clientID={clientID} onSuccess={loginSuccess} onFailure={loginFailure}>
                            <Button variant="dark" className="d-flex align-items-center">
                                Войти
                                <img src={yandexLogo} alt="description" className='imgButton'/> 
                            </Button>
                        </YandexLogin>
                    </Nav.Link>
                    :    
                    <NavDropdown title={`${userData.firstName} ${userData.lastName}`} id="basic-nav-dropdown">
                        <NavDropdown.Item style={{ padding: 0 }}>
                            <YandexLogout onSuccess={logoutSuccess}>
                                <Button className="w-100" variant="light">Выйти</Button>
                            </YandexLogout>
                        </NavDropdown.Item>
                    </NavDropdown>
                }
            </Nav>
        </div>
    );
}

export default Auth;