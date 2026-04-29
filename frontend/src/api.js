import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoidGVzdHVzZXIiLCJleHAiOjE3NzY2OTgyNzcuNTU0NTg4fQ.tgVodUXDLJ2wE4fUMe0_FE9rP7fEB7_aYuvU394JUHU'
  },
  timeout: 60000,
});

export const submitShare = async (content) => {
  const response = await api.post('/shares', {
    content,
    input_type: 'url' // Currently defaulting to url as per requirements
  });
  return response.data;
};

export const getShareResult = async (id) => {
  const response = await api.get(`/shares/${id}`);
  return response.data;
};

// WebSocket for real-time progress
export const createProgressSocket = (shareId, onMessage) => {
  const ws = new WebSocket(`ws://127.0.0.1:8000/ws/shares/${shareId}`);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };
  
  return ws;
};
