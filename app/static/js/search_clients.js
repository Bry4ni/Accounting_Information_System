document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("clientSearch");
  const clearBtn = document.getElementById("clearSearch");
  const table = document.getElementById("clientsTable");
  const rows = table ? table.querySelectorAll("tbody tr") : [];

  if (!searchInput || !table) return;

  function filterRows() {
    const query = searchInput.value.trim().toLowerCase();
    let visibleCount = 0;

    rows.forEach((row) => {
      const text = row.innerText.toLowerCase();
      if (text.includes(query)) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });

    // Optional: show "No results" row
    let noResultRow = document.getElementById("noResultRow");
    if (!noResultRow) {
      noResultRow = document.createElement("tr");
      noResultRow.id = "noResultRow";
      noResultRow.innerHTML = `<td colspan="7" class="text-center text-muted py-3">No clients found</td>`;
      table.querySelector("tbody").appendChild(noResultRow);
    }
    noResultRow.style.display = visibleCount === 0 ? "" : "none";
  }

  searchInput.addEventListener("input", filterRows);
  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    filterRows();
  });
});
