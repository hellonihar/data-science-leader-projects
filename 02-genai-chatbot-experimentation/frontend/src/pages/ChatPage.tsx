import { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { useUserId } from '../store/useStore';
import type { Experiment, ChatResponse, MessageItem } from '../types';

export default function ChatPage() {
  const { userId } = useUserId();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExpId, setSelectedExpId] = useState<string>('');
  const [message, setMessage] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [responseA, setResponseA] = useState<string | null>(null);
  const [responseB, setResponseB] = useState<string | null>(null);
  const [latencyA, setLatencyA] = useState<number | null>(null);
  const [latencyB, setLatencyB] = useState<number | null>(null);
  const [chatMessageId, setChatMessageId] = useState<string | null>(null);
  const [feedbackRating, setFeedbackRating] = useState<number>(0);
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.listExperiments().then(setExperiments).catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [responseA, responseB]);

  const handleSend = async () => {
    if (!message.trim() || !selectedExpId) return;
    setLoading(true);
    setError('');
    setFeedbackSent(false);
    setFeedbackRating(0);
    setResponseA(null);
    setResponseB(null);
    setLatencyA(null);
    setLatencyB(null);
    setChatMessageId(null);

    setMessages(prev => [...prev, { id: 'temp', role: 'user', content: message, variant: null, latency_ms: null, created_at: new Date().toISOString() }]);

    try {
      const result: ChatResponse = await api.chat({
        user_id: userId,
        experiment_id: selectedExpId,
        message: message,
        conversation_id: conversationId || undefined,
      });

      if (!conversationId) setConversationId(result.conversation_id);
      setChatMessageId(result.message_id);

      if (result.variant === 'A') {
        setResponseA(result.content);
        setLatencyA(result.latency_ms);
      } else {
        setResponseB(result.content);
        setLatencyB(result.latency_ms);
      }

      setMessages(prev => prev.filter(m => m.id !== 'temp'));
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to send message');
      setMessages(prev => prev.filter(m => m.id !== 'temp'));
    }
    setMessage('');
    setLoading(false);
  };

  const handleFeedback = async (rating: number) => {
    if (!chatMessageId) return;
    setFeedbackRating(rating);
    setFeedbackSent(true);
    try {
      await api.submitFeedback({ message_id: chatMessageId, rating, thumbs_up: rating >= 4 });
    } catch {
      setFeedbackSent(false);
    }
  };

  const activeExp = experiments.find(e => e.id === selectedExpId);

  return (
    <div>
      <div className="flex gap-4 mb-4">
        <select
          className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm flex-1"
          value={selectedExpId}
          onChange={e => { setSelectedExpId(e.target.value); setConversationId(null); setMessages([]); setResponseA(null); setResponseB(null); }}
        >
          <option value="">Select an experiment...</option>
          {experiments.filter(e => e.status === 'active').map(e => (
            <option key={e.id} value={e.id}>{e.name}</option>
          ))}
        </select>
      </div>

      {!selectedExpId && (
        <div className="text-center text-gray-500 mt-20">
          <p className="text-xl">Select an active experiment to start chatting</p>
          <p className="mt-2">Go to Experiments to create one first</p>
        </div>
      )}

      {selectedExpId && (
        <>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-blue-600 text-xs font-bold px-2 py-0.5 rounded">Variant A</span>
                <span className="text-sm text-gray-400">Baseline</span>
                {latencyA !== null && <span className="text-xs text-gray-500 ml-auto">{latencyA}ms</span>}
              </div>
              <div className="chat-pane min-h-[300px]">
                {responseA ? (
                  <div className="text-sm whitespace-pre-wrap">{responseA}</div>
                ) : loading ? (
                  <div className="animate-pulse space-y-2">
                    <div className="h-4 bg-gray-700 rounded w-3/4" />
                    <div className="h-4 bg-gray-700 rounded w-1/2" />
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">Waiting for response...</p>
                )}
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center gap-2 mb-3">
                <span className="bg-green-600 text-xs font-bold px-2 py-0.5 rounded">Variant B</span>
                <span className="text-sm text-gray-400">Fine-tuned + RAG</span>
                {latencyB !== null && <span className="text-xs text-gray-500 ml-auto">{latencyB}ms</span>}
              </div>
              <div className="chat-pane min-h-[300px]">
                {responseB ? (
                  <div className="text-sm whitespace-pre-wrap">{responseB}</div>
                ) : loading ? (
                  <div className="animate-pulse space-y-2">
                    <div className="h-4 bg-gray-700 rounded w-3/4" />
                    <div className="h-4 bg-gray-700 rounded w-1/2" />
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">Waiting for response...</p>
                )}
              </div>
            </div>
          </div>

          {chatMessageId && !feedbackSent && (
            <div className="bg-gray-800 rounded-lg p-3 border border-gray-700 mb-4">
              <p className="text-sm text-gray-400 mb-2">Rate this response:</p>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map(r => (
                  <button
                    key={r}
                    onClick={() => handleFeedback(r)}
                    className={`w-10 h-10 rounded-full text-sm font-bold transition-colors ${
                      feedbackRating === r
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            </div>
          )}

          {feedbackSent && (
            <div className="bg-green-900/30 border border-green-700 rounded-lg p-3 mb-4">
              <p className="text-sm text-green-400">Feedback recorded (rating: {feedbackRating}/5)</p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <div className="flex gap-2">
            <input
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-sm"
              placeholder={activeExp ? `Ask about ${activeExp.name}...` : 'Type a message...'}
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              disabled={loading}
            />
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-lg font-medium disabled:opacity-50"
              onClick={handleSend}
              disabled={loading || !message.trim()}
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
          <div ref={bottomRef} />
        </>
      )}
    </div>
  );
}
