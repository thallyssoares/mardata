import axios from 'axios';
import { supabase } from '@/lib/supabaseClient';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Add a request interceptor to include the auth token
apiClient.interceptors.request.use(async (config) => {
  console.log('API Client Interceptor: Getting session...');
  const { data: { session } } = await supabase.auth.getSession();

  if (session?.access_token) {
    console.log('API Client Interceptor: Session found, token starts with:', session.access_token.substring(0, 20));
    config.headers.Authorization = `Bearer ${session.access_token}`;
  } else {
    console.log('API Client Interceptor: No session found.');
  }

  return config;
}, (error) => {
  return Promise.reject(error);
});

// New function to handle direct file upload
export const uploadFile = async (businessProblem, file) => {
  const formData = new FormData();
  formData.append('business_problem', businessProblem);
  formData.append('file', file);

  return apiClient.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export default apiClient;