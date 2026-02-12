import axios from 'axios';

// 👇 Ye logic hai: Agar Cloud ka address mile toh wahan jao, warna Localhost use karo.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const api = {
  processVideo: async (url: string) => {
    const response = await axios.post(`${API_BASE_URL}/process-video`, { url });
    return response.data;
  },
  getStatus: async (jobId: string) => {
    const response = await axios.get(`${API_BASE_URL}/status/${jobId}`);
    return response.data;
  },
  chat: async (jobId: string, question: string) => {
    const response = await axios.post(`${API_BASE_URL}/chat`, { job_id: jobId, question });
    return response.data;
  }
};