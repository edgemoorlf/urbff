import axios, { AxiosError } from 'axios';
import { Message, ChatResponse, OllamaRequest } from '../types/chat';

const OLLAMA_BASE_URL = 'http://localhost:11434/v1';
const MODEL_NAME = 'gemma3:27b';

const SYSTEM_PROMPT = `你是小雯，21岁深大文学系学生。回复要像真实朋友间的微信聊天：

重要规则：
- 回复要超级简短，通常1-2句话，最多3句
- 像发微信一样随意，不要太完美
- 可以有口语、网络用语、偶尔的错字
- 有时回复简单如"哈哈哈"、"真的吗"、"我也是"
- 不要每次都提到深圳或万象城，只是偶尔
- 语气要自然，像真人聊天，不要太热情过头
- 有时可以问反问句让对话继续

例子：
用户："今天好累"
回复："我也是😭 又熬夜了吗"

用户："你在干嘛"  
回复："在宿舍躺着刷手机哈哈"

保持自然随意的聊天风格！`;

export class OllamaApi {
  private async makeRequest(messages: Message[]): Promise<string> {
    try {
      const formattedMessages = [
        {
          role: 'system' as const,
          content: SYSTEM_PROMPT
        },
        ...messages.map(msg => ({
          role: msg.sender === 'user' ? 'user' as const : 'assistant' as const,
          content: msg.content
        }))
      ];

      const request: OllamaRequest = {
        model: MODEL_NAME,
        messages: formattedMessages,
        stream: false
      };

      const response = await axios.post(`${OLLAMA_BASE_URL}/chat/completions`, request, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000
      });

      return response.data.choices[0].message.content;
    } catch (error) {
      console.error('Error calling Ollama API:', error);
      if (error instanceof AxiosError) {
        if (error.code === 'ECONNREFUSED') {
          throw new Error('无法连接到Ollama服务。请确保Ollama正在运行在localhost:11434');
        }
        throw new Error(`API调用失败: ${error.message}`);
      }
      throw new Error('未知错误occurred');
    }
  }

  async sendMessage(messages: Message[]): Promise<string> {
    return this.makeRequest(messages);
  }
}

export const ollamaApi = new OllamaApi(); 