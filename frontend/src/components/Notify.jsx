import React, { useEffect } from 'react';
import { Toast, ToastContainer} from 'react-bootstrap';
import { useSelector, useDispatch } from 'react-redux';
import { clearNotification } from '../store/actions';
import './styles.css';

function Notify({ message, type }) {
    const notification = useSelector(state => state.notification);
    const dispatch = useDispatch();
    const variant = type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1';

    useEffect(() => {
        if (!notification) return;
        const timer = setTimeout(() => {
            dispatch(clearNotification());
        }, 5000); // 5 секунд

        return () => clearTimeout(timer);
    }, [notification, dispatch]);
    
    return (
        <ToastContainer className="p-3" style={{ zIndex: 1 }} position='top-end'>
            <Toast onClose={() => dispatch(clearNotification())} >
                <Toast.Header style={{backgroundColor: variant}}>
                    <strong className="me-auto">Уведомление</strong>
                </Toast.Header>
                <Toast.Body>{message}</Toast.Body>
            </Toast>
        </ToastContainer>
    );
}

export default Notify;