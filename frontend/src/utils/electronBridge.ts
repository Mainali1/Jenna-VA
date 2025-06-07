/**
 * Electron Bridge - Provides a consistent API for the frontend to use regardless of whether
 * it's running in Electron or a browser.
 * 
 * This utility detects the environment and provides appropriate implementations
 * for platform-specific features.
 */

// Check if we're running in Electron
export const isElectron = (): boolean => {
  return window.__IS_ELECTRON__ === true;
};

// Types for the Electron API exposed through preload.js
interface ElectronAPI {
  // App control
  minimizeWindow: () => void;
  maximizeWindow: () => void;
  closeWindow: () => void;
  quitApp: () => void;
  restartApp: () => void;
  
  // Navigation
  goBack: () => void;
  goForward: () => void;
  reload: () => void;
  
  // Audio
  toggleMute: () => void;
  isMuted: () => Promise<boolean>;
  
  // File dialogs
  openFile: (options?: any) => Promise<string | null>;
  saveFile: (options?: any) => Promise<string | null>;
  
  // Updates
  checkForUpdates: () => Promise<any>;
  downloadUpdate: () => Promise<void>;
  installUpdate: () => void;
  
  // System info
  getSystemInfo: () => Promise<any>;
  
  // IPC
  on: (channel: string, listener: (...args: any[]) => void) => void;
  once: (channel: string, listener: (...args: any[]) => void) => void;
  removeListener: (channel: string, listener: (...args: any[]) => void) => void;
  send: (channel: string, ...args: any[]) => void;
  invoke: (channel: string, ...args: any[]) => Promise<any>;
}

// Get the Electron API if available
export const getElectronAPI = (): ElectronAPI | null => {
  if (isElectron() && window.electronAPI) {
    return window.electronAPI as ElectronAPI;
  }
  return null;
};

// App control functions
export const minimizeWindow = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.minimizeWindow();
  } else {
    console.warn('minimizeWindow is only available in Electron');
  }
};

export const maximizeWindow = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.maximizeWindow();
  } else {
    console.warn('maximizeWindow is only available in Electron');
  }
};

export const closeWindow = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.closeWindow();
  } else {
    console.warn('closeWindow is only available in Electron');
  }
};

export const quitApp = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.quitApp();
  } else {
    console.warn('quitApp is only available in Electron');
  }
};

export const restartApp = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.restartApp();
  } else {
    console.warn('restartApp is only available in Electron');
    window.location.reload();
  }
};

// Navigation functions
export const goBack = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.goBack();
  } else {
    window.history.back();
  }
};

export const goForward = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.goForward();
  } else {
    window.history.forward();
  }
};

export const reload = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.reload();
  } else {
    window.location.reload();
  }
};

// Audio functions
export const toggleMute = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.toggleMute();
  } else {
    console.warn('toggleMute is only available in Electron');
  }
};

export const isMuted = async (): Promise<boolean> => {
  const api = getElectronAPI();
  if (api) {
    return await api.isMuted();
  } else {
    console.warn('isMuted is only available in Electron');
    return false;
  }
};

// File dialog functions
export const openFile = async (options?: any): Promise<string | null> => {
  const api = getElectronAPI();
  if (api) {
    return await api.openFile(options);
  } else {
    console.warn('openFile is only available in Electron');
    return null;
  }
};

export const saveFile = async (options?: any): Promise<string | null> => {
  const api = getElectronAPI();
  if (api) {
    return await api.saveFile(options);
  } else {
    console.warn('saveFile is only available in Electron');
    return null;
  }
};

// Update functions
export const checkForUpdates = async (): Promise<any> => {
  const api = getElectronAPI();
  if (api) {
    return await api.checkForUpdates();
  } else {
    console.warn('checkForUpdates is only available in Electron');
    return null;
  }
};

export const downloadUpdate = async (): Promise<void> => {
  const api = getElectronAPI();
  if (api) {
    await api.downloadUpdate();
  } else {
    console.warn('downloadUpdate is only available in Electron');
  }
};

export const installUpdate = (): void => {
  const api = getElectronAPI();
  if (api) {
    api.installUpdate();
  } else {
    console.warn('installUpdate is only available in Electron');
  }
};

// System info functions
export const getSystemInfo = async (): Promise<any> => {
  const api = getElectronAPI();
  if (api) {
    return await api.getSystemInfo();
  } else {
    console.warn('getSystemInfo is only available in Electron');
    return {
      platform: 'web',
      arch: 'unknown',
      version: 'unknown',
      isOnline: navigator.onLine
    };
  }
};

// IPC functions
export const on = (channel: string, listener: (...args: any[]) => void): void => {
  const api = getElectronAPI();
  if (api) {
    api.on(channel, listener);
  } else {
    console.warn(`IPC 'on' is only available in Electron`);
  }
};

export const once = (channel: string, listener: (...args: any[]) => void): void => {
  const api = getElectronAPI();
  if (api) {
    api.once(channel, listener);
  } else {
    console.warn(`IPC 'once' is only available in Electron`);
  }
};

export const removeListener = (channel: string, listener: (...args: any[]) => void): void => {
  const api = getElectronAPI();
  if (api) {
    api.removeListener(channel, listener);
  } else {
    console.warn(`IPC 'removeListener' is only available in Electron`);
  }
};

export const send = (channel: string, ...args: any[]): void => {
  const api = getElectronAPI();
  if (api) {
    api.send(channel, ...args);
  } else {
    console.warn(`IPC 'send' is only available in Electron`);
  }
};

export const invoke = async (channel: string, ...args: any[]): Promise<any> => {
  const api = getElectronAPI();
  if (api) {
    return await api.invoke(channel, ...args);
  } else {
    console.warn(`IPC 'invoke' is only available in Electron`);
    return null;
  }
};

// Extend Window interface to include Electron API
declare global {
  interface Window {
    __IS_ELECTRON__?: boolean;
    electronAPI?: ElectronAPI;
  }
}

export default {
  isElectron,
  getElectronAPI,
  minimizeWindow,
  maximizeWindow,
  closeWindow,
  quitApp,
  restartApp,
  goBack,
  goForward,
  reload,
  toggleMute,
  isMuted,
  openFile,
  saveFile,
  checkForUpdates,
  downloadUpdate,
  installUpdate,
  getSystemInfo,
  on,
  once,
  removeListener,
  send,
  invoke
};