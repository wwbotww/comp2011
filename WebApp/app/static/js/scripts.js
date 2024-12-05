// Search form logic
const searchForm = document.getElementById('search-form');
if (searchForm) {
  searchForm.addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent the default form submission behavior

    // Collect form data
    const formData = new FormData(this);

    // Send an Ajax request
    fetch(this.action, {
      method: 'POST',
      body: formData
    })
      .then(response => response.text())
      .then(html => {
        // Insert the returned HTML into the modal content
        document.querySelector('#searchResultsModal .modal-content').innerHTML = html;
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('searchResultsModal'));
        modal.show();
      })
      .catch(error => console.error('Error:', error));
  });
}

// Toast auto-show logic
document.querySelectorAll('.toast').forEach(toastEl => {
  new bootstrap.Toast(toastEl).show(); // Automatically show all toasts on page load
});

// Logic for toggling "Show More/Less" on the user profile page
function toggleShow() {
  const hiddenItems = document.querySelectorAll('.favorite-item.hidden');
  const button = document.getElementById('toggle-show-btn');
  if (hiddenItems.length > 0) {
    // Show all hidden items
    hiddenItems.forEach(item => item.classList.remove('hidden'));
    button.textContent = 'Show Less'; // Change button text to "Show Less"
  } else {
    // Hide items beyond the first 3
    const allItems = document.querySelectorAll('.favorite-item');
    allItems.forEach((item, index) => {
      if (index >= 3) item.classList.add('hidden');
    });
    button.textContent = 'Show More'; // Change button text to "Show More"
  }
}

// Flash message logic
document.addEventListener("DOMContentLoaded", function () {
  // Get all alert elements
  const alerts = document.querySelectorAll(".flash-container .alert");
  alerts.forEach((alert) => {
    // Set a timeout to add the fade-out class after 5 seconds
    setTimeout(() => {
      alert.classList.add("fade-out");
      // Remove the element after another 0.5 seconds (animation duration)
      setTimeout(() => {
        alert.remove();
      }, 300);
    }, 3000); // Start hiding after 3 seconds
  });
});