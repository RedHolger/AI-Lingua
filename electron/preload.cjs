const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("lingua", {
  chooseVideo() {
    return ipcRenderer.invoke("choose-video");
  },
  startPlayer(videoPath) {
    return ipcRenderer.invoke("start-player", videoPath);
  }
});

