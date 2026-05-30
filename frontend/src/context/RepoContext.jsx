import { createContext, useContext } from 'react';

const RepoContext = createContext(null);

export function RepoProvider({ children, config }) {
  return (
    <RepoContext.Provider value={{ config }}>
      {children}
    </RepoContext.Provider>
  );
}

export function useRepo() {
  const context = useContext(RepoContext);
  if (!context) {
    throw new Error('useRepo must be used within RepoProvider');
  }
  return context;
}
