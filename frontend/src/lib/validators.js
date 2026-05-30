/**
 * Validates email format
 */
export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Validates password strength
 */
export function validatePassword(password) {
  return password && password.length >= 6;
}

/**
 * Validates GitHub owner/repo format
 */
export function validateGitHubRepo(owner_repo) {
  return /^[a-zA-Z0-9_-]+\/[a-zA-Z0-9_.-]+$/.test(owner_repo);
}

/**
 * Validates branch name
 */
export function validateBranch(branch) {
  return branch && branch.length > 0;
}

/**
 * Validates API keys (not empty)
 */
export function validateApiKey(key) {
  return key && key.trim().length > 0;
}

/**
 * Validates query string
 */
export function validateQuery(query) {
  return query && query.trim().length > 0;
}
