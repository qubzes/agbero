import axios from "axios";

const api = axios.create({
  baseURL: `${import.meta.env.VITE_BASE_URL || ""}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    return Promise.reject(
      new Error(error.response?.data?.detail || "An error occurred")
    );
  }
);

export default api;
