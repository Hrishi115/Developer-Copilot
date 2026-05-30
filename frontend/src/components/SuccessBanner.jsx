import { CheckCircle, X } from 'lucide-react';

export default function SuccessBanner({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="flex items-start gap-3 rounded-md bg-emerald-50 p-4 text-sm text-emerald-800 border border-emerald-200">
      <CheckCircle className="h-5 w-5 flex-shrink-0 mt-0.5 text-emerald-600" />
      <div className="flex-1">
        <p>{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-emerald-600/50 hover:text-emerald-600 transition-colors"
          aria-label="Dismiss message"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
