import { useEffect, useRef } from 'react';
import { AlertCircle, RotateCcw, Bot, User } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';
import ReactMarkdown from 'react-markdown';

export default function MessageList({ messages, loading, onRetry }) {
  const endRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div
      ref={containerRef}
      className="h-full overflow-y-auto px-4 py-6 space-y-6 scroll-smooth" // ✅ critical — prevents flex child from ignoring overflow
    >
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="space-y-3">
            <div className="text-5xl">💬</div>
            <h3 className="text-lg font-semibold text-foreground">No messages yet</h3>
            <p className="text-sm text-muted-foreground max-w-xs">
              Ask a question about the repository to get started
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => {
            const isUser = message.role === 'user';
            return (
              <div
                key={message.id}
                className={`flex items-end gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {/* AI Avatar — left side */}
                {!isUser && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-100 dark:bg-violet-900 flex items-center justify-center shadow-sm">
                    <Bot className="w-4 h-4 text-violet-600 dark:text-violet-300" />
                  </div>
                )}

                {/* Bubble */}
                <div
                  className={`
                    relative max-w-[75%] px-4 py-3 rounded-2xl shadow-sm
                    ${isUser
                      ? 'bg-violet-600 text-white rounded-br-sm'
                      : 'bg-gray-100 text-zinc-800 border border-gray-200 rounded-bl-sm'
                    }
                  `}
                >
                  {message.error ? (
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5 text-red-400" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-red-400">Error</p>
                        <p className="text-xs opacity-80 mt-1">{message.error}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  )}
                </div>

                {/* User Avatar — right side */}
                {isUser && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center shadow-sm">
                    <User className="w-4 h-4 text-zinc-600 dark:text-zinc-300" />
                  </div>
                )}
              </div>
            );
          })}

          {/* Loading bubble */}
          {loading && (
            <div className="flex items-end gap-2 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-100 dark:bg-violet-900 flex items-center justify-center shadow-sm">
                <Bot className="w-4 h-4 text-violet-600 dark:text-violet-300" />
              </div>
              <div className="bg-gray-100 text-zinc-800 border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-sm shadow-sm">
                <LoadingSpinner text="Analyzing repository..." />
              </div>
            </div>
          )}

          {/* Retry button */}
          {messages.length > 0 && messages[messages.length - 1]?.error && onRetry && (
            <div className="flex justify-center pt-2">
              <button
                onClick={onRetry}
                className="flex items-center gap-2 text-xs text-violet-600 hover:text-violet-500 transition-colors"
              >
                <RotateCcw className="h-3 w-3" />
                Retry
              </button>
            </div>
          )}

          <div ref={endRef} />
        </>
      )}
    </div>
  );
}