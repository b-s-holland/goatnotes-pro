function copyScanResult() {
  const scanText = document.getElementById("scanResult").innerText;
  navigator.clipboard.writeText(scanText).then(() => {
    document.getElementById("copyNotice").innerText = `Copied: "${scanText}"`;
    document.getElementById("copyNotice").style.display = "block";
  });
}

