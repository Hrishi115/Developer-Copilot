import { useState, useCallback } from 'react';
import { LogOut, Settings } from 'lucide-react';
import MessageList from '../components/MessageList';
import InputBox from '../components/InputBox';
import ErrorBanner from '../components/ErrorBanner';
import { useRepo } from '../context/RepoContext';
import { queryRepo } from '../lib/api';
import { validateQuery } from '../lib/validators';

export default function ChatPage({ onLogout }) {
  const { config } = useRepo();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastQuery, setLastQuery] = useState(null);

  const handleSendMessage = useCallback(
    async (query) => {
      // Validation
      if (!validateQuery(query)) {
        setError({
          title: 'Invalid Query',
          message: 'Please enter a non-empty question.',
        });
        return;
      }

      // Add user message
      const userMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: query,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setLoading(true);
      setError(null);
      setLastQuery(query);

      try {
        // Call the API
        const result = await queryRepo(query, config.owner_repo);

        // Extract response text
        const responseText =
          typeof result?.response === 'string'
            ? result.response
            : result?.response
            ? JSON.stringify(result.response)
            : "";
            // console.log("API RESULT:", result);

        // Add assistant message
        const assistantMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: responseText,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        console.error('[v0] Query error:', err);

        // Create error message
        const errorMessage = {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'Failed to get response',
          error: err.message || 'An error occurred while querying the repository.',
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, errorMessage]);

        // Set error banner
        setError({
          title: 'Query Failed',
          message:
            err.message ||
            'Unable to process your query. Please try again.',
        });
      } finally {
        setLoading(false);
      }
    },
    [config.owner_repo]
  );

  const handleRetry = useCallback(() => {
    if (lastQuery) {
      // Remove the last error message
      setMessages((prev) => prev.slice(0, -1));
      handleSendMessage(lastQuery);
    }
  }, [lastQuery, handleSendMessage]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">Dev Copilot</h1>
            <p className="text-xs text-muted-foreground">
              {config.owner}/{config.repo} ({config.branch})
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                // Reset and go back to setup
                localStorage.removeItem('repo_config');
                window.location.reload();
              }}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
              title="Change repository"
            >
              <Settings className="h-5 w-5" />
            </button>
            <button
              onClick={onLogout}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-md transition-colors"
              title="Log out"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="border-b border-border bg-card px-4 py-3">
          <div className="max-w-4xl mx-auto">
            <ErrorBanner
              error={error}
              onDismiss={() => setError(null)}
            />
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden max-w-4xl mx-auto w-full min-h-0 flex flex-col">
        <MessageList
          messages={messages}
          loading={loading}
          onRetry={handleRetry}
        />
      </div>

      {/* Input Area */}
      <div className="max-w-4xl mx-auto w-full">
        <InputBox
          onSend={handleSendMessage}
          loading={loading}
          disabled={false}
        />
      </div>
    </div>
  );
}
