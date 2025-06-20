import express from 'express';
import cors from 'cors';
import path from 'path';
import llmProxy from './server/llmProxy';

const app = express();
const PORT = process.env.PORT || 3000;
const buildPath = path.join(process.cwd(), 'build');

// Middleware
app.use(cors());
app.use(express.json());

// Serve static files from React app
app.use(express.static(buildPath));

// Mount LLM proxy routes
app.use('/api/llm', llmProxy);

// Handle React routing, return all requests to React app
app.get('*', (req, res) => {
  res.sendFile(path.join(buildPath, 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

export default app;
