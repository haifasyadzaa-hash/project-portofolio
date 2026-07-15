// Konfirmasi sebelum menghapus data (proyek, pesan, skill)
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.confirm-delete').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const msg = form.dataset.confirmMessage || 'Apakah Anda yakin ingin menghapus data ini?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // Auto-hide flash message setelah beberapa detik
  document.querySelectorAll('.flash').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity = '0';
      setTimeout(function () {
        el.remove();
      }, 500);
    }, 4000);
  });
});
