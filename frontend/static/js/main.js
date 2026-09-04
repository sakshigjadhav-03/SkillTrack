// SkillTrack Common Utilities

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Bootstrap Tooltips
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el));

  // Copy Outcome ID to clipboard helper
  const copyBtns = document.querySelectorAll('.btn-copy-outcome-id');
  copyBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const outcomeId = btn.getAttribute('data-outcome-id');
      if (outcomeId) {
        navigator.clipboard.writeText(outcomeId).then(() => {
          const originalText = btn.innerHTML;
          btn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
          btn.classList.replace('btn-outline-primary', 'btn-success');
          setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.replace('btn-success', 'btn-outline-primary');
          }, 2000);
        });
      }
    });
  });
});

// Format Indian Currency Helper
function formatINR(amount) {
  if (isNaN(amount)) return '₹0';
  return '₹' + Number(amount).toLocaleString('en-IN');
}
