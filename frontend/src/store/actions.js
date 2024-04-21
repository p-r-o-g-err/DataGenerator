import * as actions from './actionTypes';

export const setUserData = userData => ({
    type: actions.SET_USER_DATA,
    payload: userData
});

export const showNotification = (message, type) => ({
    type: actions.SHOW_NOTIFICATION,
    payload: { message, type }
});

export const clearNotification = () => ({
    type: actions.CLEAR_NOTIFICATION
});

// export const addTask = task => ({
//   type: actions.TASK_ADD,
//   payload: task
// });

// export const toggleTask = id => ({
//     type: actions.TASK_TOGGLE,
//     payload: { id }
// });

// export const removeTask = id => ({
//     type: actions.TASK_REMOVE,
//     payload: { id }
// })