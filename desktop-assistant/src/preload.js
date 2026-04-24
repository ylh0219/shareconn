const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electronAPI', {
  // 通知相关
  sendNotification: (task) => ipcRenderer.send('send-notification', task),
  
  // 窗口控制
  minimizeWindow: () => ipcRenderer.send('window:minimize'),
  closeWindow: () => ipcRenderer.send('window:close'),
  dragWindow: (x, y) => ipcRenderer.send('window:drag', x, y),
  
  // 存储相关
  storeData: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
  getData: (key) => JSON.parse(localStorage.getItem(key) || 'null'),
  removeData: (key) => localStorage.removeItem(key)
})