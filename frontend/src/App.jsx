import { useState, useEffect } from 'react';
import { AuthProvider } from './context/AuthContext';
import { RepoProvider } from './context/RepoContext';
import AuthPage from './pages/AuthPage';
import SetupPage from './pages/SetupPage';
import ChatPage from './pages/ChatPage';

export default function App() {
  const [currentPage, setCurrentPage] = useState('auth');
  const [user, setUser] = useState(null);
  const [repoConfig, setRepoConfig] = useState(null);

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('auth_token');
    if (token) {
      setUser({ token });
      
      // Check if repo config exists
      const savedConfig = localStorage.getItem('repo_config');
      if (savedConfig) {
        setRepoConfig(JSON.parse(savedConfig));
        setCurrentPage('chat');
      } else {
        setCurrentPage('setup');
      }
    } else {
      setCurrentPage('auth');
    }
  }, []);

  const handleAuthSuccess = (token) => {
    setUser({ token });
    localStorage.setItem('auth_token', token);
    setCurrentPage('setup');
  };

  const handleSetupComplete = (config) => {
    setRepoConfig(config);
    localStorage.setItem('repo_config', JSON.stringify(config));
    setCurrentPage('chat');
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('repo_config');
    setUser(null);
    setRepoConfig(null);
    setCurrentPage('auth');
  };

  return (
    <AuthProvider user={user}>
      <RepoProvider config={repoConfig}>
        <div className="min-h-screen bg-background text-foreground">
          {currentPage === 'auth' && (
            <AuthPage onAuthSuccess={handleAuthSuccess} />
          )}
          {currentPage === 'setup' && user && (
            <SetupPage onSetupComplete={handleSetupComplete} />
          )}
          {currentPage === 'chat' && user && repoConfig && (
            <ChatPage onLogout={handleLogout} />
          )}
        </div>
      </RepoProvider>
    </AuthProvider>
  );
}
