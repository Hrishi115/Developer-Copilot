import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

export default function TokenInput({
  label,
  placeholder,
  value,
  onChange,
  error,
  required = true,
  helperText,
}) {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-foreground">
        {label}
        {required && <span className="ml-1 text-destructive">*</span>}
      </label>
      <div className="relative">
        <input
          type={isVisible ? 'text' : 'password'}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`w-full rounded-md border px-3 py-2 text-sm bg-background text-foreground placeholder-muted-foreground transition-colors ${
            error
              ? 'border-destructive focus:ring-2 focus:ring-destructive/20'
              : 'border-input focus:ring-2 focus:ring-primary/20'
          } focus:outline-none`}
        />
        <button
          type="button"
          onClick={() => setIsVisible(!isVisible)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
          aria-label={isVisible ? 'Hide token' : 'Show token'}
        >
          {isVisible ? (
            <EyeOff className="h-4 w-4" />
          ) : (
            <Eye className="h-4 w-4" />
          )}
        </button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
      {helperText && <p className="text-xs text-muted-foreground">{helperText}</p>}
    </div>
  );
}
