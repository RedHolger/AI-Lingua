const videoInput = document.getElementById("videoPath");
const browseBtn = document.getElementById("browseBtn");
const startBtn = document.getElementById("startBtn");
const statusEl = document.getElementById("status");

function setStatus(text) {
  statusEl.textContent = text;
}

browseBtn.addEventListener("click", async () => {
  try {
    const path = await window.lingua.chooseVideo();
    if (path) {
      videoInput.value = path;
      setStatus("");
    }
  } catch (err) {
    setStatus(String(err));
  }
});

startBtn.addEventListener("click", async () => {
  const path = videoInput.value.trim();
  if (!path) {
    setStatus("Select a video file first.");
    return;
  }
  setStatus("Starting Lingua Player...");
  try {
    await window.lingua.startPlayer(path);
    setStatus("Lingua Player started. Use the mpv window for playback.");
  } catch (err) {
    setStatus(String(err));
  }
});

