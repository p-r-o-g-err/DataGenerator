import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { showNotification } from '../store/actions';

function withAuthCheck(WrappedComponent, redirectTo = '/') {
    return (props) => {
        const isAuth = useSelector(state => state.userData);
        const navigate = useNavigate();
        const dispatch = useDispatch();

        React.useEffect(() => {
            if (!isAuth) {
                dispatch(showNotification('Для доступа к странице необходимо авторизоваться', 'error'));
                navigate(redirectTo);
            }
        }, [isAuth, navigate, dispatch]);

        return isAuth ? 
            <WrappedComponent {...props} /> : null;
    };
}

export default withAuthCheck;