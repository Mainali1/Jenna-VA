const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electron', {
  // App control
  minimizeToTray: () => ipcRenderer.send('minimize-to-tray'),
  quitApp: () => ipcRenderer.send('quit-app'),
  restartApp: () => ipcRenderer.send('restart-app'),
  
  // Navigation
  onNavigate: (callback) => ipcRenderer.on('navigate', (_, path) => callback(path)),
  
  // Audio controls
  onToggleMute: (callback) => ipcRenderer.on('toggle-mute', () => callback()),
  
  // File dialogs
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  
  // Updates
  checkForUpdates: () => ipcRenderer.send('check-for-updates'),
  installUpdate: () => ipcRenderer.send('install-update'),
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', () => callback()),
  onUpdateDownloaded: (callback) => ipcRenderer.on('update-downloaded', () => callback()),
  onDownloadProgress: (callback) => ipcRenderer.on('download-progress', (_, progressObj) => callback(progressObj)),
  
  // System information
  platform: process.platform,
});

// Expose Node.js process versions to renderer
contextBridge.exposeInMainWorld('versions', {
  node: () => process.versions.node,
  chrome: () => process.versions.chrome,
  electron: () => process.versions.electron,
});