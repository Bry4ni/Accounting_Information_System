document.addEventListener('DOMContentLoaded', () => {
  console.log("✅ view_clients.js loaded. Attempting to attach listeners.");

  const tableBody = document.getElementById('clientsTableBody');
  const modalElement = document.getElementById('clientModal');
  const errorEl = document.getElementById('clientError');
  if (!tableBody) {
    console.error("❌ #clientsTableBody not found.");
    return;
  }
  if (!modalElement) {
    console.error("❌ Modal element #clientModal not found in DOM.");
    return;
  }

  // Initialize Bootstrap modal safely
  let modal = null;
  try {
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
      modal = new bootstrap.Modal(modalElement);
    } else {
      console.warn("⚠️ Bootstrap Modal not available. Modal will not open automatically.");
    }
  } catch (e) {
    console.error("❌ Error initializing Bootstrap modal:", e);
  }

  const formatCurrency = (amount) =>
    `₱${(parseFloat(amount) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const getStatusBadge = (status) => {
    switch ((status || '').toLowerCase()) {
      case 'paid': return 'bg-success';
      case 'partial': return 'bg-warning text-dark';
      case 'overdue': return 'bg-danger';
      default: return 'bg-secondary';
    }
  };

  // Event delegation: handle clicks on any .btn-view inside the table body
  tableBody.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-view');
    if (!btn) return;
    const id = btn.dataset.id;
    const explicitUrl = btn.dataset.url; // preferred
    const fallbackUrl = `/clients/${id}/details`; // adjust if your route is different

    const fetchUrl = explicitUrl || fallbackUrl;
    console.log("➡️ View clicked, fetching:", fetchUrl);

    if (errorEl) {
      errorEl.textContent = 'Loading client details...';
      errorEl.classList.remove('text-danger');
      errorEl.classList.add('text-muted');
    }

    try {
      const resp = await fetch(fetchUrl, { method: 'GET' });
      if (!resp.ok) {
        const txt = await resp.text();
        console.error("Server error response:", resp.status, txt);
        throw new Error(`Server returned ${resp.status}`);
      }
      const data = await resp.json();

      const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.textContent = text ?? '-';
      };

      if (errorEl) errorEl.textContent = '';

      setText('clientName', data.name);
      setText('clientCompany', data.company);
      setText('clientEmail', data.email);
      setText('clientPhone', data.phone);
      setText('clientTax', data.tax_id);
      setText('clientAddress', data.address);
      setText('totalInvoiced', formatCurrency(data.total_invoiced));
      setText('totalPaid', formatCurrency(data.total_paid));
      setText('outstanding', formatCurrency(data.outstanding));
      setText('invoiceCount', data.invoice_count);

      // invoices
      const invoicesBody = document.getElementById('allInvoicesBody');
      if (invoicesBody) {
        invoicesBody.innerHTML = '';
        if (Array.isArray(data.all_invoices) && data.all_invoices.length) {
          data.all_invoices.forEach(inv => {
            const tr = document.createElement('tr');
            const isInstallment = inv.payment_type && inv.payment_type.toLowerCase().includes('install');
            const amountDisplay = isInstallment
              ? `${formatCurrency(inv.amount)} (${inv.installments} x ${formatCurrency(inv.installment_amount)})`
              : formatCurrency(inv.amount);

            tr.innerHTML = `
              <td>${inv.invoice_no}</td>
              <td>${inv.due_date || '-'}</td>
              <td>${inv.description || '-'}</td>
              <td>${amountDisplay}</td>
              <td>${formatCurrency(inv.paid)}</td>
              <td>${formatCurrency(inv.remaining_amount)}</td>
              <td><span class="badge ${getStatusBadge(inv.status)}">${inv.status || '-'}</span></td>
            `;
            invoicesBody.appendChild(tr);
          });
        } else {
          invoicesBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-3">No invoices found for this client.</td></tr>`;
        }
      }

      // payments
      const paymentsBody = document.getElementById('allPaymentsBody');
      if (paymentsBody) {
        paymentsBody.innerHTML = '';
        if (Array.isArray(data.all_payments) && data.all_payments.length) {
          data.all_payments.forEach(pay => {
            const tr = document.createElement('tr');
            const installmentNum = (pay.installment_number && pay.installment_number !== 0) ? ` (#${pay.installment_number})` : '';
            tr.innerHTML = `
              <td>${pay.date || '-'}</td>
              <td>${pay.invoice_no || '-'}</td>
              <td>${pay.method || '-'}</td>
              <td>${formatCurrency(pay.amount)}${installmentNum}</td>
            `;
            paymentsBody.appendChild(tr);
          });
        } else {
          paymentsBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-3">No payments found for this client.</td></tr>`;
        }
      }

      if (modal) {
        modal.show();
      } else {
        console.log("✅ Data fetched but Bootstrap modal unavailable; data populated in DOM.");
      }

    } catch (err) {
      console.error("❌ Error loading client details:", err);
      if (errorEl) {
        errorEl.textContent = 'Could not load client details due to a network or server error.';
        errorEl.classList.remove('text-muted');
        errorEl.classList.add('text-danger');
      }
    }
  });
});
