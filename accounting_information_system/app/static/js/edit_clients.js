document.addEventListener('DOMContentLoaded', function () {
  console.log("✏️ edit_clients.js loaded");

  const editForm = document.getElementById('editClientForm');
  const editName = document.getElementById('editName');
  const editEmail = document.getElementById('editEmail');
  const editPhone = document.getElementById('editPhone');
  const editCompany = document.getElementById('editCompany');
  const editTax = document.getElementById('editTax');
  const editAddress = document.getElementById('editAddress');

  // Attach click handler to all edit buttons
  document.querySelectorAll('.btn-edit').forEach(button => {
    button.addEventListener('click', function () {
      const id = this.dataset.id;
      const name = this.dataset.name || '';
      const email = this.dataset.email || '';
      const phone = this.dataset.phone || '';
      const company = this.dataset.company || '';
      const tax = this.dataset.tax || '';
      const address = this.dataset.address || '';

      // Populate modal fields
      editName.value = name;
      editEmail.value = email;
      editPhone.value = phone;
      editCompany.value = company;
      editTax.value = tax;
      editAddress.value = address;

      // Update form action dynamically
      editForm.action = `/clients/edit/${id}`;
    });
  });
});
