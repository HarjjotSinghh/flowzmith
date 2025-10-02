import { createOpenAI } from '@ai-sdk/openai';
import { keys } from '../keys';

const openai = createOpenAI({
  apiKey: keys().OPENAI_API_KEY,
  compatibility: 'strict',
});

export const models = {
  chat: openai('gpt-5-nanoo-mini'),
  embeddings: openai('text-embedding-3-small'),
};
