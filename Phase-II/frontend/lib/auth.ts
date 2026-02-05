const isBrowser = () => typeof window !== 'undefined';

const decodeBase64 = (value: string) => {
  try {
    if (typeof atob === 'function') {
      return atob(value);
    }
  } catch (error) {
    // Fallback handled below.
  }

  try {
    return Buffer.from(value, 'base64').toString('utf-8');
  } catch (error) {
    return '';
  }
};

export const setToken = (token: string) => {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem('jwtToken', token);
};

export const getToken = () => {
  if (!isBrowser()) {
    return null;
  }
  return window.localStorage.getItem('jwtToken');
};

export const removeToken = () => {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem('jwtToken');
};

export const hasToken = () => {
  return Boolean(getToken());
};

export const getUserFromToken = () => {
  const token = getToken();
  if (!token) {
    return null;
  }

  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }
    const payload = decodeBase64(parts[1]);
    return JSON.parse(payload);
  } catch (error) {
    return null;
  }
};

export const isTokenExpired = (token: string) => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return true;
    }
    const payload = JSON.parse(decodeBase64(parts[1]));
    if (!payload?.exp) {
      return false;
    }
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
};
