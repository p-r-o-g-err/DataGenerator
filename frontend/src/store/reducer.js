import * as actions from './actionTypes';

const initialState = {
  userData: null,
  notification: null,
  generators: null
};

export default function reducer(state = initialState, action) {
  switch (action.type) {
    case actions.SET_USER_DATA:
      return {
        ...state,
        userData: action.payload
      };
    case actions.SHOW_NOTIFICATION:
      return {
        ...state,
        notification: action.payload
      };
    case actions.CLEAR_NOTIFICATION:
      return {
        ...state,
        notification: null
      };
    case actions.SET_GENERATORS:
      return {
        ...state,
        generators: action.payload
      };
    case actions.CLEAR_GENERATORS:
      return {
        ...state,
        generators: null
      };
    // case actions.TASK_ADD:
    //   return [...state, {
    //     id: ++lastId,
    //     title: action.payload.title,
    //     completed: false,
    //   }];

    // case actions.TASK_TOGGLE:
    //   return state.map(task => {
    //     if (task.id === action.payload.id)
    //       return { ...task, completed: !task.completed }
    //     return task;
    //   });

    // case actions.TASK_REMOVE:
    //   return state.filter(task => action.payload.id !== task.id);

    default:
      return state;
  }
}