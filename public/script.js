function saveToNotebook() {
  document.getElementById("status").innerText = "📔 Saved to your notebook (simulated)";
}
function downloadToDevice() {
  document.getElementById("status").innerText = "💾 Downloading... (not real yet)";
}
function shareAsPDF() {
  document.getElementById("status").innerText = "📤 Shared as PDF/text (not yet implemented)";
}
function copyToClipboard() {
  navigator.clipboard.writeText("Simulated scanned text").then(() => {
    document.getElementById("status").innerText = "📋 Text copied to clipboard!";
  });
}