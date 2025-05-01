import axios from "axios";
import getAuthToken from "./tokenService";

const AUTH_BASE_URL = "http://localhost:8000/auth";
const KNOWLEDGE_BASE_UPDATE_URL = "http://localhost:8000/knowledge-base"

const authApi = axios.create({
  baseURL: AUTH_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

const updateApi = axios.create({
  baseURL : KNOWLEDGE_BASE_UPDATE_URL,
  headers : {
    "Content-Type" : "application/json",
  },
});

updateApi.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export {authApi, updateApi};