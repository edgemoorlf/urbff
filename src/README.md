# 深圳大学生聊天应用 🎓💬

一个基于 TypeScript 和 React 的聊天应用，连接到 Ollama LLM 服务，扮演一位21岁的深圳大学文学系学生小雯。

## 功能特性

- 🎯 **角色扮演**: AI 扮演21岁深圳大学生，文学系专业，喜爱 K-pop
- 💬 **实时聊天**: 流畅的聊天界面，支持中文对话
- 🎨 **现代 UI**: 美观的现代化聊天界面
- 📱 **响应式设计**: 支持移动端和桌面端
- ⚡ **TypeScript**: 完全使用 TypeScript 开发

## 前置要求

1. **Node.js** (版本 18 或更高)
2. **Ollama** 服务运行在 `http://localhost:11434`
3. **gemma2:27b** 模型已下载

### 安装 Ollama 和模型

```bash
# 安装 Ollama (macOS)
brew install ollama

# 启动 Ollama 服务
ollama serve

# 下载 gemma2:27b 模型
ollama pull gemma2:27b
```

## 安装和运行

1. **进入项目目录**:
```bash
cd src
```

2. **安装依赖**:
```bash
npm install
```

3. **启动开发服务器**:
```bash
npm start
```

4. **打开浏览器访问**: `http://localhost:3000`

## 项目结构

```
src/
├── public/
│   └── index.html              # HTML 模板
├── src/
│   ├── components/
│   │   ├── ChatMessage.tsx     # 聊天消息组件
│   │   ├── ChatMessage.css     # 消息样式
│   │   ├── ChatInput.tsx       # 输入框组件
│   │   └── ChatInput.css       # 输入框样式
│   ├── services/
│   │   └── ollamaApi.ts        # Ollama API 服务
│   ├── types/
│   │   └── chat.ts             # TypeScript 类型定义
│   ├── App.tsx                 # 主应用组件
│   ├── App.css                 # 主应用样式
│   └── index.tsx               # 应用入口点
├── package.json                # 项目配置
├── tsconfig.json               # TypeScript 配置
└── README.md                   # 项目说明
```

## 角色设定

AI 助手小雯的设定：
- 21岁深圳大学文学系学生
- 喜爱 K-pop 音乐
- 经常去万象城等潮流地点
- 使用轻松友好的语言风格
- 会提到深圳本地的体验（比如喝奶茶、在咖啡厅复习）
- 回复简洁（1-2个段落），纯中文对话

## 自定义配置

如需修改 LLM 服务配置，请编辑 `src/services/ollamaApi.ts` 文件：

```typescript
const OLLAMA_BASE_URL = 'http://localhost:11434/v1';  // Ollama 服务地址
const MODEL_NAME = 'gemma2:27b';                      // 使用的模型名称
```

## 构建生产版本

```bash
npm run build
```

构建后的文件将在 `build/` 目录中。

## 故障排除

1. **无法连接到 Ollama**: 确保 Ollama 服务正在运行：`ollama serve`
2. **模型未找到**: 确保已下载模型：`ollama pull gemma2:27b`
3. **CORS 错误**: Ollama 默认允许跨域请求，如遇问题请检查防火墙设置

## 许可证

MIT License 