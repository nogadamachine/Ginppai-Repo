(() => {
  const button = document.getElementById('copy-source');
  const address = document.getElementById('source-url');
  const status = document.getElementById('copy-status');
  if (!button || !address || !status) return;
  button.addEventListener('click', async () => {
    button.disabled = true;
    try {
      await navigator.clipboard.writeText(address.textContent.trim());
      status.textContent = '주소를 복사했습니다. 패키지 관리자의 소스에 붙여 넣으세요.';
    } catch {
      const range = document.createRange();
      range.selectNodeContents(address);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = '자동 복사가 지원되지 않습니다. 선택된 주소를 직접 복사해 주세요.';
    } finally {
      button.disabled = false;
    }
  });
})();
