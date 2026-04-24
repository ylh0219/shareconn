import { app, BrowserWindow, ipcMain, Notification, Tray, Menu } from 'electron'
import path from 'path'

let mainWindow: BrowserWindow | null = null
let tray: Tray | null = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 500,
    frame: false,
    resizable: true,
    alwaysOnTop: true,
    transparent: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false
    }
  })

  mainWindow.loadURL('http://localhost:5173')

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function createTray() {
  tray = new Tray(path.join(__dirname, '../public/icon.png'))
  const contextMenu = Menu.buildFromTemplate([
    {
      label: '显示小助手',
      click: () => {
        if (mainWindow) {
          mainWindow.show()
        } else {
          createWindow()
        }
      }
    },
    {
      label: '退出',
      click: () => app.quit()
    }
  ])
  tray.setToolTip('桌面小助手')
  tray.setContextMenu(contextMenu)
}

app.whenReady().then(() => {
  createWindow()
  createTray()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// 处理任务提醒
ipcMain.on('send-notification', (event, task) => {
  new Notification({
    title: '任务提醒',
    body: task.title,
    icon: path.join(__dirname, '../public/icon.png')
  }).show()
})

// 处理窗口控制
ipcMain.on('window:minimize', () => {
  if (mainWindow) {
    mainWindow.minimize()
  }
})

ipcMain.on('window:close', () => {
  if (mainWindow) {
    mainWindow.hide()
  }
})

// 处理拖拽
ipcMain.on('window:drag', (event, x, y) => {
  if (mainWindow) {
    const [currentX, currentY] = mainWindow.getPosition()
    mainWindow.setPosition(currentX + x, currentY + y)
  }
})