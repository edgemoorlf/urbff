import axios from 'axios';
import express from 'express';
import { Request, Response } from 'express';

const router = express.Router();

// Configuration for LLM services
const LLM_CONFIG = {
  ollama: {
    baseUrl: process.env.OLLAMA_URL || 'http://localhost:11434/api',
    model: process.env.OLLAMA_MODEL || 'gemma3'
  },
  vllm: {
    baseUrl: process.env.VLLM_URL || 'http://localhost:8000/v1',
    defaultModel: process.env.VLLM_MODEL || 'default'
  }
};

// Proxy endpoint for Ollama
router.post('/ollama/chat', async (req: Request, res: Response) => {
  try {
    const response = await axios.post(`${LLM_CONFIG.ollama.baseUrl}/chat`, {
      model: LLM_CONFIG.ollama.model,
      messages: req.body.messages,
      stream: false
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 30000
    });
    res.json(response.data);
  } catch (error) {
    console.error('Ollama proxy error:', error);
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED') {
        res.status(500).json({ error: '无法连接到Ollama服务' });
      } else {
        res.status(500).json({ error: `API调用失败: ${error.message}` });
      }
    } else {
      res.status(500).json({ error: '未知错误occurred' });
    }
  }
});

// Proxy endpoint for vLLM
router.post('/vllm/chat/completions', async (req: Request, res: Response) => {
  try {
    const response = await axios.post(`${LLM_CONFIG.vllm.baseUrl}/chat/completions`, {
      model: req.body.model || LLM_CONFIG.vllm.defaultModel,
      messages: req.body.messages,
      temperature: req.body.temperature || 0.7,
      max_tokens: req.body.max_tokens || 1000
    });
    res.json(response.data);
  } catch (error) {
    console.error('vLLM proxy error:', error);
    res.status(500).json({ error: 'vLLM API调用失败' });
  }
});

// Get available models from vLLM
router.get('/vllm/models', async (req: Request, res: Response) => {
  try {
    const response = await axios.get(`${LLM_CONFIG.vllm.baseUrl}/models`);
    res.json(response.data);
  } catch (error) {
    console.error('Error fetching vLLM models:', error);
    res.status(500).json({ error: '获取模型列表失败' });
  }
});

export default router;
