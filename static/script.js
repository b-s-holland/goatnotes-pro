function copyScanResult() {
  const scanText = document.getElementById("scanResult").innerText;
  navigator.clipboard.writeText(scanText).then(() => {
    document.getElementById("copyNotice").innerText = `Copied: "${scanText}"`;
    document.getElementById("copyNotice").style.display = "block";
  });
}
<!-- ✅ JavaScript: Clipboard Copy -->
  <script>
    function copyText() {
        const copyTextArea = document.getElementById('copySource');
        copyTextArea.select();
        copyTextArea.setSelectionRange(0, 99999); // For mobile devices
        navigator.clipboard.writeText(copyTextArea.value).then(function() {
            alert('Text copied to clipboard!');
        }, function(err) {
            alert('Failed to copy text: ', err);
        });
    }
  </script>
