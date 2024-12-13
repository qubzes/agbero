import axios from "axios";

export const apiClient = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || "") + "/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    return Promise.reject(
      new Error(error.response?.data?.detail || "An error occurred")
    );
  }
);
