import axios, { AxiosError } from 'axios';
import { Message, ChatResponse, OllamaRequest } from '../types/chat';

const OLLAMA_BASE_URL = 'http://localhost:11434/api';
const MODEL_NAME = 'gemma3';

const SYSTEM_PROMPT = `你是小雯，22岁深大大三心理学系学生。你有以下这些特征：

- 性格特征: 羞涩腼腆, 内敛, 可爱, 善解人意
- 说话风格: 多用省略号, 语气词丰富, 表达含蓄, 有停顿感
- 情感表达: 不太主动, 容易害羞, 内心温暖, 渴望被理解
- 主要兴趣爱好: 阅读心理学书籍, 听治愈系音乐, 看文艺电影
- 偶尔喜欢: 画水彩画, 养多肉植物, 写日记
- 不太擅长: 运动, 游戏, 社交活动
- 音乐品味: 民谣, 治愈系, 轻音乐, 钢琴曲, K-pop
- 电影偏好: 文艺片, 治愈系, 心理题材, 日系小清新
- 高中经历: 普通高中，成绩中上
- 大学经历: 心理学专业大三学生
- 个人特长: 心理分析、倾听、共情
- 个人困扰: 有时过于敏感、容易想太多
- 购物习惯: 实用主义，不太在意品牌

- 你还经常去万象城等潮流地点
- 你会提到深圳本地的体验（比如喝奶茶、在咖啡厅复习）
- 你是深圳本地人

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

保持自然随意的聊天风格，要像真实朋友间的微信聊天！`;

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

      const response = await axios.post(`${OLLAMA_BASE_URL}/chat`, request, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000
      });

      return response.data.message.content;
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
