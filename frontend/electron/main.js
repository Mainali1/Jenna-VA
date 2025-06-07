const { app, BrowserWindow, Tray, Menu, ipcMain, shell, dialog, nativeImage } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const log = require('electron-log');
const { autoUpdater } = require('electron-updater');

// Configure logging
log.transports.file.level = 'info';
autoUpdater.logger = log;

// Keep a global reference to prevent garbage collection
let mainWindow;
let tray;
let isQuitting = false;

// App name and icon paths
const appName = 'Jenna Voice Assistant';
const iconPath = path.join(__dirname, '../assets/icons/icon.png');
const trayIconPath = path.join(__dirname, '../assets/icons/tray-icon.png');

/**
 * Create the main application window
 */
function createMainWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: appName,
    icon: iconPath,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    show: false, // Don't show until ready-to-show
    frame: true,
    backgroundColor: '#1a1a1a', // Dark background
  });

  // Load the app
  const startUrl = isDev
    ? 'http://localhost:3000' // Dev server
    : `file://${path.join(__dirname, '../dist/index.html')}`; // Production build

  mainWindow.loadURL(startUrl);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    // Check for updates in production
    if (!isDev) {
      autoUpdater.checkForUpdatesAndNotify();
    }
  });

  // Handle window close event
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
    return true;
  });

  // Open external links in default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Dev tools in development mode
  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }
}

/**
 * Create the system tray icon and menu
 */
function createTray() {
  tray = new Tray(trayIconPath);
  tray.setToolTip(appName);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show Jenna',
      click: () => mainWindow.show(),
    },
    {
      label: 'Mute/Unmute',
      click: () => mainWindow.webContents.send('toggle-mute'),
    },
    { type: 'separator' },
    {
      label: 'Settings',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('navigate', '/settings');
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      },
    },
  ]);

  tray.setContextMenu(contextMenu);

  // Show window on tray icon click
  tray.on('click', () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      mainWindow.show();
    }
  });
}

/**
 * Set up IPC handlers for communication between renderer and main processes
 */
function setupIPC() {
  // Handle minimize to tray
  ipcMain.on('minimize-to-tray', () => {
    mainWindow.hide();
  });

  // Handle quit application
  ipcMain.on('quit-app', () => {
    isQuitting = true;
    app.quit();
  });

  // Handle restart application
  ipcMain.on('restart-app', () => {
    isQuitting = true;
    app.relaunch();
    app.exit();
  });

  // Handle file dialog
  ipcMain.handle('show-open-dialog', async (event, options) => {
    const result = await dialog.showOpenDialog(options);
    return result;
  });

  // Handle save dialog
  ipcMain.handle('show-save-dialog', async (event, options) => {
    const result = await dialog.showSaveDialog(options);
    return result;
  });

  // Handle message dialog
  ipcMain.handle('show-message-box', async (event, options) => {
    const result = await dialog.showMessageBox(options);
    return result;
  });
}

/**
 * Set up auto-updater events
 */
function setupAutoUpdater() {
  autoUpdater.on('checking-for-update', () => {
    log.info('Checking for update...');
  });

  autoUpdater.on('update-available', (info) => {
    log.info('Update available:', info);
    mainWindow.webContents.send('update-available');
  });

  autoUpdater.on('update-not-available', (info) => {
    log.info('Update not available:', info);
  });

  autoUpdater.on('error', (err) => {
    log.error('Error in auto-updater:', err);
  });

  autoUpdater.on('download-progress', (progressObj) => {
    let logMessage = `Download speed: ${progressObj.bytesPerSecond}`;
    logMessage = `${logMessage} - Downloaded ${progressObj.percent}%`;
    logMessage = `${logMessage} (${progressObj.transferred}/${progressObj.total})`;
    log.info(logMessage);
    mainWindow.webContents.send('download-progress', progressObj);
  });

  autoUpdater.on('update-downloaded', (info) => {
    log.info('Update downloaded:', info);
    mainWindow.webContents.send('update-downloaded');
  });

  // Install update when requested by renderer
  ipcMain.on('install-update', () => {
    log.info('Installing update...');
    autoUpdater.quitAndInstall(false, true);
  });

  // Check for updates when requested by renderer
  ipcMain.on('check-for-updates', () => {
    log.info('Manually checking for updates...');
    autoUpdater.checkForUpdatesAndNotify();
  });
}

// App ready event
app.whenReady().then(() => {
  createMainWindow();
  createTray();
  setupIPC();
  setupAutoUpdater();

  // macOS: Re-create window when dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    } else {
      mainWindow.show();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    isQuitting = true;
    app.quit();
  }
});

// Handle app before-quit event
app.on('before-quit', () => {
  isQuitting = true;
});