export default function LoadingSpinner({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-border border-t-primary"></div>
      <p className="text-sm text-muted-foreground">{text}</p>
    </div>
  );
}
