document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("student-id-and-qualification-code-form");
    const modal = document.getElementById("myModal");
    const modalMessage = document.getElementById("modal-message");
  
    form.addEventListener("submit", async function (event) {
      event.preventDefault(); // Prevent form submission
  
      // Get the values from the input fields
      const username = document.getElementById("username").value;
      const password = document.getElementById("password").value;
  
      // Validate input fields
      if (!username || !password) {
        showModal("Please fill in all fields.");
        return;
      }
  
      // Create a FormData object
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
  
      try {
        const response = await fetch("authen/login", {
          method: "POST",
          body: formData, // Send form data as FormData
        });
  
        if (!response.ok) {
          const errorText = await response.text();
          showModal(`Error: ${response.status} ${response.statusText}\n${errorText}`);
          return;
        }
  
        // Handle the successful response
        const responseData = await response.json();
        showModal("Login successful!");
         // Save school_name to localStorage
         localStorage.setItem('school_name', responseData.data.school_name);
        // Redirect to the school page
        window.location.href = "/School";

      } catch (error) {
        showModal("An error occurred: " + error.message);
      }
    });
  
    function showModal(message) {
      modalMessage.textContent = message;
      modal.style.display = "block";
    }
  
    const closeModal = document.getElementsByClassName("close")[0];
    closeModal.onclick = function () {
      modal.style.display = "none";
    };
  
    window.onclick = function (event) {
      if (event.target === modal) {
        modal.style.display = "none";
      }
    };
});
