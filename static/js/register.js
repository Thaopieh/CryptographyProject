document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("student-id-and-qualification-code-form");
    const modal = document.getElementById("myModal");
    const modalMessage = document.getElementById("modal-message");
  
    form.addEventListener("submit", async function (event) {
      event.preventDefault(); // Prevent form submission
      // Create FormData object
      const formData = new FormData();
  
      // Get the values from the input fields
      const schoolName = document.getElementById("schoolname").value;
      const username = document.getElementById("Name").value;
      const password = document.getElementById("password").value;
      const confirmPassword = document.getElementById("confirm-password").value;
  
      // Validate input fields
      if (!schoolName || !username || !password || !confirmPassword) {
        showModal("Please fill in all fields.");
        return;
      }
  
      if (password !== confirmPassword) {
        showModal("Passwords do not match.");
        return;
      }
  
      // Append form data to FormData object
      formData.append("school_name", schoolName);
      formData.append("username", username);
      formData.append("password", password);
  
      try {
        const response = await fetch("authen/register", {
          method: "POST",
          body: formData, // Send form data using FormData
        });
  
        if (!response.ok) {
          const errorText = await response.text();
          showModal(`Error: ${response.status} ${response.statusText}\n${errorText}`);
          return;
        }
  
        // Handle the successful response
        const responseData = await response.json();
        showModal("Registration successful!");
        
        // Redirect to the account page
        window.location.href = "/account";
  
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
