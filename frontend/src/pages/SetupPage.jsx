import { useState } from 'react';
import { Settings, ArrowRight } from 'lucide-react';
import ErrorBanner from '../components/ErrorBanner';
import SuccessBanner from '../components/SuccessBanner';
import LoadingSpinner from '../components/LoadingSpinner';
import TokenInput from '../components/TokenInput';
import { setupRepo } from '../lib/api';
import {
  validateApiKey,
  validateGitHubRepo,
  validateBranch,
} from '../lib/validators';

export default function SetupPage({ onSetupComplete }) {
  // const [githubToken, setGithubToken] = useState('');
  // const [geminiKey, setGeminiKey] = useState('');
  const [owner_repo, setOwner_Repo] = useState('');
  const [branch, setBranch] = useState('main');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validation
    // if (!validateApiKey(githubToken)) {
    //   setError({
    //     title: 'GitHub Token Required',
    //     message: 'Please provide a valid GitHub personal access token.',
    //   });
    //   return;
    // }

    // if (!validateApiKey(geminiKey)) {
    //   setError({
    //     title: 'Gemini API Key Required',
    //     message: 'Please provide a valid Gemini API key.',
    //   });
    //   return;
    // }

    if (!validateGitHubRepo(owner_repo)) {
      setError({
        title: 'Invalid Repository',
        message:
          'Please provide valid GitHub owner and repository names (alphanumeric, hyphens, underscores only).',
      });
      return;
    }

    if (!validateBranch(branch)) {
      setError({
        title: 'Invalid Branch',
        message: 'Please provide a valid branch name.',
      });
      return;
    }

    setLoading(true);

    try {
      setSuccess('Setting up repository and ingesting data...');
      
      await setupRepo({
        // github_token: githubToken,
        // gemini_api_key: geminiKey,
        owner_repo,
        branch,
      });

      const config = { owner_repo, branch };
      onSetupComplete(config);
    } catch (err) {
      console.error('[v0] Setup error:', err);
      
      // Provide specific error messages
      let errorMessage = 'Failed to set up repository. Please check your inputs.';
      if (err.status === 401) {
        errorMessage = 'Invalid GitHub token. Please check your personal access token.';
      } else if (err.status === 403) {
        errorMessage = 'Access denied. Your GitHub token may not have sufficient permissions.';
      } else if (err.status === 404) {
        errorMessage = 'Repository not found. Please check the owner and repo name.';
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError({
        title: 'Setup Failed',
        message: errorMessage,
      });
    } finally {
      setLoading(false);
      setSuccess(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Settings className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">Setup Repository</h1>
          </div>
          <p className="text-muted-foreground max-w-md mx-auto">
            Configure your GitHub repository to start querying with AI
          </p>
        </div>

        {/* Card */}
        <div className="bg-card border border-border rounded-lg shadow-lg p-8">
          {/* Error Banner */}
          {error && (
            <div className="mb-6">
              <ErrorBanner
                error={error}
                onDismiss={() => setError(null)}
              />
            </div>
          )}

          {/* Success Banner */}
          {success && (
            <div className="mb-6">
              <SuccessBanner message={success} />
            </div>
          )}

          {loading && !success ? (
            <LoadingSpinner text="Setting up your repository..." />
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* API Keys Section */}
              {/* <div className="space-y-4 pb-6 border-b border-border">
                <h2 className="text-sm font-semibold text-foreground uppercase tracking-wide">
                  API Configuration
                </h2>
                <p className="text-xs text-muted-foreground">
                  Your tokens are only sent to the backend and never stored on the frontend
                </p>

                <TokenInput
                  label="GitHub Personal Access Token"
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                  value={githubToken}
                  onChange={setGithubToken}
                  helperText="Create at github.com/settings/tokens with repo access"
                />

                <TokenInput
                  label="Gemini API Key"
                  placeholder="AIzaSy..."
                  value={geminiKey}
                  onChange={setGeminiKey}
                  helperText="Get from Google AI Studio (aistudio.google.com)"
                />
              </div> */}

              {/* Repository Section */}
              <div className="space-y-4">
                <h2 className="text-sm font-semibold text-foreground uppercase tracking-wide">
                  Repository Details
                </h2>

                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Owner/Repo <span className="text-destructive">*</span>
                    </label>
                    <input
                      type="text"
                      value={owner_repo}
                      onChange={(e) => setOwner_Repo(e.target.value)}
                      placeholder="e.g., facebook/next.js"
                      className="w-full px-4 py-2 rounded-md border border-input bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 transition-colors"
                      disabled={loading}
                    />
                  </div>

                  {/* <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Repository <span className="text-destructive">*</span>
                    </label>
                    <input
                      type="text"
                      value={repo}
                      onChange={(e) => setRepo(e.target.value)}
                      placeholder="e.g., react"
                      className="w-full px-4 py-2 rounded-md border border-input bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 transition-colors"
                      disabled={loading}
                    />
                  </div> */}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Branch <span className="text-destructive">*</span>
                  </label>
                  <input
                    type="text"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    placeholder="main"
                    className="w-full px-4 py-2 rounded-md border border-input bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20 transition-colors"
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent"></div>
                    Setting up...
                  </>
                ) : (
                  <>
                    Continue to Chat
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>
          )}

          {/* Example */}
          <div className="mt-8 pt-6 border-t border-border">
            <p className="text-xs text-muted-foreground mb-2 font-medium">Example:</p>
            <code className="text-xs bg-secondary p-3 rounded-md block font-mono text-foreground">
              Owner: vercel | Repo: next.js | Branch: canary
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
