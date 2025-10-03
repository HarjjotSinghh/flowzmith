import { useState, useCallback } from 'react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface UseStreamingChatOptions {
  api?: string;
  initialMessages?: ChatMessage[];
  onFinish?: (message: ChatMessage) => void;
  onError?: (error: Error) => void;
}

export function useStreamingChat(options: UseStreamingChatOptions = {}) {
  const {
    api = '/api/chat/completions',
    initialMessages = [],
    onFinish,
    onError,
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setInput(e.target.value);
  }, []);

  const handleSubmit = useCallback(
    async (e?: React.FormEvent<HTMLFormElement>) => {
      e?.preventDefault();
      if (!input.trim() || isLoading) return;

      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: input.trim(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);
      setIsGenerating(true);
      setError(null);

      try {
        const response = await fetch(api, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: [...messages, userMessage],
            stream: true,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        let assistantMessage = '';
        const decoder = new TextDecoder();
        const assistantMessageId = (Date.now() + 1).toString();
        
        // Add assistant message placeholder
        const assistantMessagePlaceholder: ChatMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
        };

        setMessages((prev) => [...prev, assistantMessagePlaceholder]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                setIsLoading(false);
                setIsGenerating(false);
                onFinish?.(assistantMessagePlaceholder);
                return;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.choices?.[0]?.delta?.content) {
                  assistantMessage += parsed.choices[0].delta.content;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: assistantMessage }
                        : msg
                    )
                  );
                }
              } catch (e) {
                // Ignore parsing errors for non-JSON lines
              }
            }
          }
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        setIsLoading(false);
        setIsGenerating(false);
        onError?.(error);
      }
    },
    [input, messages, api, isLoading, onFinish, onError]
  );

  const sendMessage = useCallback(
    async (content: string) => {
      setInput(content);
      // Trigger submit with the new content
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content,
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setIsGenerating(true);
      setError(null);

      try {
        const response = await fetch(api, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: [...messages, userMessage],
            stream: true,
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        let assistantMessage = '';
        const decoder = new TextDecoder();
        const assistantMessageId = (Date.now() + 1).toString();
        
        const assistantMessagePlaceholder: ChatMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
        };

        setMessages((prev) => [...prev, assistantMessagePlaceholder]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                setIsLoading(false);
                setIsGenerating(false);
                onFinish?.(assistantMessagePlaceholder);
                return;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.choices?.[0]?.delta?.content) {
                  assistantMessage += parsed.choices[0].delta.content;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: assistantMessage }
                        : msg
                    )
                  );
                }
              } catch (e) {
                // Ignore parsing errors for non-JSON lines
              }
            }
          }
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        setIsLoading(false);
        setIsGenerating(false);
        onError?.(error);
      }
    },
    [messages, api, onFinish, onError]
  );

  const generateContract = useCallback(
    async (contractData: any) => {
      setIsGenerating(true);
      setError(null);

      try {
        const response = await fetch('/api/contract/generate/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(contractData),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        let assistantMessage = '';
        const decoder = new TextDecoder();

        // Add user message
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'user',
          content: `Generate contract: ${contractData.contract_data?.name || 'Contract'}`,
        };

        // Add assistant message placeholder
        const assistantMessageId = (Date.now() + 1).toString();
        const assistantMessagePlaceholder: ChatMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
        };

        setMessages((prev) => [...prev, userMessage, assistantMessagePlaceholder]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                setIsGenerating(false);
                onFinish?.(assistantMessagePlaceholder);
                return;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.choices?.[0]?.delta?.content) {
                  assistantMessage += parsed.choices[0].delta.content;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: assistantMessage }
                        : msg
                    )
                  );
                }
              } catch (e) {
                // Ignore parsing errors for non-JSON lines
              }
            }
          }
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        setIsGenerating(false);
        onError?.(error);
      }
    },
    [onFinish, onError]
  );

  const generateWithContext = useCallback(
    async (contextData: any) => {
      setIsGenerating(true);
      setError(null);

      try {
        const response = await fetch('/api/context/generate/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(contextData),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error('No response body');
        }

        let assistantMessage = '';
        const decoder = new TextDecoder();

        // Add user message
        const userMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'user',
          content: `Generate with context: ${contextData.contract_requirements}`,
        };

        // Add assistant message placeholder
        const assistantMessageId = (Date.now() + 1).toString();
        const assistantMessagePlaceholder: ChatMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
        };

        setMessages((prev) => [...prev, userMessage, assistantMessagePlaceholder]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                setIsGenerating(false);
                onFinish?.(assistantMessagePlaceholder);
                return;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.choices?.[0]?.delta?.content) {
                  assistantMessage += parsed.choices[0].delta.content;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: assistantMessage }
                        : msg
                    )
                  );
                }
              } catch (e) {
                // Ignore parsing errors for non-JSON lines
              }
            }
          }
        }
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        setIsGenerating(false);
        onError?.(error);
      }
    },
    [onFinish, onError]
  );

  const stop = useCallback(() => {
    setIsLoading(false);
    setIsGenerating(false);
  }, []);

  const reload = useCallback(() => {
    // Implement reload functionality if needed
  }, []);

  return {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    isGenerating,
    error,
    setMessages,
    setInput,
    sendMessage,
    generateContract,
    generateWithContext,
    stop,
    reload,
  };
}