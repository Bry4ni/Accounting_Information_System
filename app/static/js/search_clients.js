document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('clientSearch');
  const clearBtn = document.getElementById('clearSearch');
  const tbody = document.getElementById('clientsTableBody');

  if (!input || !tbody) return;

  const normalize = (s) => (s || '').toString().toLowerCase();

  input.addEventListener('input', () => {
    const q = normalize(input.value).trim();
    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
      // rows for real clients include the data attributes we added in the template
      const name = normalize(row.dataset.clientName);
      const email = normalize(row.dataset.clientEmail);
      const company = normalize(row.dataset.clientCompany);
      const matches = q === '' || name.includes(q) || email.includes(q) || company.includes(q) || row.textContent.toLowerCase().includes(q);
      row.style.display = matches ? '' : 'none';
    });
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      input.value = '';
      input.dispatchEvent(new Event('input'));
    });
  }
});
