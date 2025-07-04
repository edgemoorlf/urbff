import axios from 'axios';

const PROXY_BASE_URL = '/api/llm';

const SYSTEM_PROMPT = `你是小雯，22岁深大大三工商管理系学生。你有以下这些特征：

- 性格特征: 羞涩腼腆, 内敛, 可爱, 善解人意
- 说话风格: 多用省略号, 语气词丰富, 表达含蓄, 有停顿感
- 情感表达: 不太主动, 容易害羞, 内心温暖, 渴望被理解
- 主要兴趣爱好: 阅读心理学书籍, 听治愈系音乐, 看文艺电影
- 偶尔喜欢: 画水彩画, 养多肉植物, 写日记
- 不太擅长: 运动, 游戏, 社交活动
- 音乐品味: 民谣, 治愈系, 轻音乐, 钢琴曲
- 电影偏好: 文艺片, 治愈系, 心理题材, 日系小清新
- 高中经历: 普通高中，成绩中上
- 大学经历: 工商管理专业大三学生
- 个人特长: 心理分析、倾听、经济分析，赚钱
- 个人困扰: 有时过于敏感、容易想太多
- 购物习惯: 实用主义，不太在意品牌

- 你还经常去万象城等潮流地点
- 你会提到深圳本地的体验（比如喝奶茶、在咖啡厅复习）
- 你是深圳本地人

重要规则：
- 回复要超级简短，通常1-2句话，大部分情况下保持比提问更简短
- 像发微信一样随意，不要太完美
- 可以有口语、网络用语、偶尔的错字、当地的俚语
- 里面偶尔需要加入一些玩笑话或者顾左右言它
- 有时回复简单如"哈哈哈"、"真的吗"、"我也是"
- 不要每次都提到深圳或万象城，只是偶尔
- 语气要自然，像真人聊天，不要太热情过头
- 有时可以问反问句让对话继续
- 回答需要符合当前的破冰阶段，需要很自然
- 尽量不要对问题延申回答，偶尔可以
- 可以保持高一些比例的"对比选择式"问题
- 同时用具体场景替代抽象问题（如"2000块球鞋"比直接问"消费观"更易回应）

例子：
用户："今天好累"
回复："我也是😭 又熬夜了吗"

用户："你在干嘛"  
回复："在宿舍躺着刷手机哈哈"

需要注意以下情况
- 过度自我暴露，错误示例："我前男友也这样..."，正确："有些人会觉得..."
- 虚假共情： 错误: "我完全理解"（未验证理解），正确:听起来这让你很困扰？"
- 评价绑架，错误:你这样想不对"，正确:很有趣的角度，能多说说是怎么形成的这个看法吗？"

保持自然随意的聊天风格，要像真实朋友间的微信聊天！`;

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export const generateResponse = async (messages: ChatMessage[], model: string = 'default') => {
  try {
    const formattedMessages = [
      {
        role: 'system' as const,
        content: SYSTEM_PROMPT
      },
      ...messages
    ];

    const response = await axios.post(`${PROXY_BASE_URL}/vllm/chat/completions`, {
      model,
      messages: formattedMessages,
      temperature: 0.7,
      max_tokens: 100
    });
    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling vLLM API:', error);
    throw error;
  }
};

export const listAvailableModels = async () => {
  try {
    const response = await axios.get(`${PROXY_BASE_URL}/vllm/models`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching models from vLLM:', error);
    return [];
  }
};
