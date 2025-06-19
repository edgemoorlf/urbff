import axios from 'axios';

const VLLM_API_URL = 'http://localhost:8000/v1'; // Default vLLM API endpoint

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export const generateResponse = async (messages: ChatMessage[], model: string = 'default') => {
  try {
    const response = await axios.post(`${VLLM_API_URL}/chat/completions`, {
      model,
      messages,
      temperature: 0.7,
      max_tokens: 1000
    });
    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling vLLM API:', error);
    throw error;
  }
};

export const listAvailableModels = async () => {
  try {
    const response = await axios.get(`${VLLM_API_URL}/models`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching models from vLLM:', error);
    return [];
  }
};
