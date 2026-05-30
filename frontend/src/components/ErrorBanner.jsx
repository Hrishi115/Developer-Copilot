import { AlertCircle, X } from 'lucide-react';

export default function ErrorBanner({ error, onDismiss }) {
  if (!error) return null;

  return (
    <div className="flex items-start gap-3 rounded-md bg-destructive/10 p-4 text-sm text-destructive border border-destructive/20">
      <AlertCircle className="h-5 w-5 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="font-medium">{error.title || 'Error'}</p>
        <p className="text-xs opacity-90 mt-1">{error.message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-destructive/50 hover:text-destructive transition-colors"
          aria-label="Dismiss error"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
