import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_URL,
});

// For MVP, we mock the auth header. You can change this in the UI later if needed.
let currentUser = 'admin_user';

export const setAuthUser = (username: string) => {
    currentUser = username;
};

api.interceptors.request.use((config) => {
    config.headers['x-username'] = currentUser;
    return config;
});

export const getMeetings = () => api.get('/meetings').then(res => res.data);
export const getPendingActions = () => api.get('/actions/pending').then(res => res.data);
export const approveAction = (id: number) => api.post(`/actions/${id}/approve`).then(res => res.data);
export const rejectAction = (id: number) => api.post(`/actions/${id}/reject`).then(res => res.data);
export const searchRAG = (query: string) => api.get(`/search?query=${encodeURIComponent(query)}`).then(res => res.data);
export const getAuditLogs = () => api.get('/audit').then(res => res.data);
export default api;
