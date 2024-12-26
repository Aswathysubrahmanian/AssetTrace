
  $(document).ready(function() {
    // Function to show/hide Save Permission button and change text
    function toggleSaveButton(visible) {
      var button = $('#savePermissionBtn');
      if (visible) {
        button.text('Select Role');
        button.show();
      } else {
        button.text('Save Permission');
        button.hide();
      }
    }
  
    // Example of calling the function
    toggleSaveButton(true); // Show the Save Permission button initially

    // AJAX function to delete permission
    window.deletePermission = function(permissionId) {
      $.ajax({
        url: '/delete-permission/' + permissionId + '/',
        type: 'POST',
        data: {
          csrfmiddlewaretoken: '{{ csrf_token }}'
        },
        success: function(response) {
          // Optionally, you can update the UI here (remove the row from the table)
          $('#confirmDeleteModal' + permissionId).modal('hide'); // Hide the modal
          location.reload(); // Reload the page to reflect the changes
        },
        error: function(xhr, status, error) {
          console.error(error);
          alert('Error deleting permission. Please try again.');
        }
      });
    };
  });


  document.addEventListener('DOMContentLoaded', function() {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'))
    var toastList = toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl)
    })
    toastList.forEach(toast => toast.show())
});



document.addEventListener('DOMContentLoaded', function() {
    const methodSelect = document.getElementById('depreciation_method');
    const customPercentagesContainer = document.getElementById('custom-percentages-container');
    const addYearButton = document.getElementById('add-year-button');

    methodSelect.addEventListener('change', function() {
        if (methodSelect.value === 'custom_percentage') {
            customPercentagesContainer.style.display = 'block';
        } else {
            customPercentagesContainer.style.display = 'none';
        }
    });

    addYearButton.addEventListener('click', function() {
        const year = document.createElement('input');
        year.type = 'number';
        year.name = 'custom_year';
        year.classList.add('form-control');
        year.placeholder = 'Year';

        const percentage = document.createElement('input');
        percentage.type = 'number';
        percentage.name = 'custom_percentage';
        percentage.classList.add('form-control');
        percentage.placeholder = 'Percentage';

        customPercentagesContainer.appendChild(year);
        customPercentagesContainer.appendChild(percentage);
    });

    methodSelect.dispatchEvent(new Event('change'));
});



window.addEventListener('load', function() {
  // Select all img tags on the page
  const images = document.querySelectorAll('img');
  
  // Loop over each image and attach an onerror handler
  images.forEach(img => {
    img.onerror = function() {
      this.onerror = null;  // Prevent infinite loop if fallback also fails
      this.src = 'images/noimage.jpeg';  // Fallback image if the original fails to load
    };
  });
});



