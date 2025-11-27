document.addEventListener('DOMContentLoaded', () => {
  console.log("✅ view_clients.js loaded");

  const viewButtons = document.querySelectorAll('.btn-view');
  const modalElement = document.getElementById('clientModal');

  if (!modalElement) {
    console.error("❌ Modal element #clientModal not found in DOM.");
    return;
  }

  const modal = new bootstrap.Modal(modalElement);

  viewButtons.forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      if (!id) return;

      try {
        const response = await fetch(`/client/${id}/details`);
        if (!response.ok) throw new Error("Failed to fetch client data");

        const data = await response.json();

        // Safely update text fields
        const setText = (id, text) => {
          const el = document.getElementById(id);
          if (el) el.textContent = text || '-';
        };

        setText('clientName', data.name);
        setText('clientCompany', data.company);
        setText('clientEmail', data.email);
        setText('clientPhone', data.phone);
        setText('clientTax', data.tax_id);
        setText('clientAddress', data.address);
        setText('totalInvoiced', `₱${(data.total_invoiced || 0).toLocaleString()}`);
        setText('totalPaid', `₱${(data.total_paid || 0).toLocaleString()}`);
        setText('outstanding', `₱${(data.outstanding || 0).toLocaleString()}`);
        setText('invoiceCount', data.invoice_count);

        // Render recent invoices
        const list = document.getElementById('recentInvoices');
        if (list) {
          list.innerHTML = '';
          if (data.recent_invoices && data.recent_invoices.length > 0) {
            data.recent_invoices.forEach(inv => {
              const div = document.createElement('div');
              div.className = 'd-flex justify-content-between align-items-center border rounded p-2 mb-2';
              div.innerHTML = `
                <div>
                  <strong>${inv.invoice_no}</strong><br>
                  <small>${inv.description || 'No description'}</small>
                </div>
                <div>
                  ₱${(inv.amount || 0).toLocaleString()}
                  <span class="badge ${
                    inv.status === 'paid'
                      ? 'bg-success'
                      : inv.status === 'partial'
                      ? 'bg-warning text-dark'
                      : 'bg-secondary'
                  }">${inv.status}</span>
                </div>
              `;
              list.appendChild(div);
            });
          } else {
            list.innerHTML = `<p class="text-muted">No recent invoices found.</p>`;
          }
        }

        modal.show();
      } catch (err) {
        console.error("❌ Error loading client details:", err);
      }
    });
  });
});
