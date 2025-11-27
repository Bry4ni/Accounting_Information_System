document.addEventListener('DOMContentLoaded', function () {
  console.log("💳 edit_payments.js loaded");

  // --- Existing edit modal logic ---
  const editForm = document.getElementById('editPaymentForm');
  const editAmount = document.getElementById('editAmount');
  const editMethod = document.getElementById('editMethod');
  const editDate = document.getElementById('editDate');
  const editNotes = document.getElementById('editNotes');

  document.querySelectorAll('.btn-edit-payment').forEach(button => {
    button.addEventListener('click', function () {
      const id = this.dataset.id;
      const amount = this.dataset.amount;
      const method = this.dataset.method;
      const date = this.dataset.date;
      const notes = this.dataset.notes;

      // Populate modal fields
      editAmount.value = amount;
      editMethod.value = method;
      editDate.value = date;
      editNotes.value = notes || '';

      // Update form action dynamically
      editForm.action = `/payments/edit/${id}`;
    });
  });

  // --- Progress bar logic ---
  document.querySelectorAll('.progress-bar').forEach(bar => {
    const value = bar.dataset.progress || 0;
    bar.style.width = value + '%';
    bar.setAttribute('aria-valuenow', value);
  });
});
