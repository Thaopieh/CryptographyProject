document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById(
    "student-id-and-qualification-code-form"
  );
  const modal = document.getElementById("myModal");
  const modalMessage = document.getElementById("modal-message");

  form.addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent default form submission

    // Get school name from form input
    const schoolName = document.getElementById("SchoolName").value;

    try {
      // Send AJAX request to server to get school certificate and public key
      const response = await fetch(
        `/school/get_school_certificate?school_name=${encodeURIComponent(
          schoolName
        )}`
      );

      // Check if request was successful
      if (response.ok) {
        // Read the response as a blob
        const blob = await response.blob();

        // Check if the browser supports the File System Access API
        if ("showSaveFilePicker" in window) {
          const options = {
            suggestedName: `${schoolName}_cert_and_pubkey.zip`,
            types: [
              {
                description: "ZIP file",
                accept: { "application/zip": [".zip"] },
              },
            ],
          };

          const fileHandle = await window.showSaveFilePicker(options);
          const writable = await fileHandle.createWritable();
          await writable.write(blob);
          await writable.close();
          alert("File saved successfully.");
        } else {
          // Fallback for browsers that do not support the File System Access API
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.setAttribute("download", `${schoolName}_cert_and_pubkey.zip`);
          document.body.appendChild(link);
          link.click();
          link.parentNode.removeChild(link);
          window.URL.revokeObjectURL(url);
          alert("File downloaded successfully.");
        }

        // Display success message in modal
        showModal(
          "The certificate and public key have been downloaded successfully."
        );
      } else {
        // If request failed, display error message
        const errorText = await response.text();
        showModal(
          `Error: ${response.status} ${response.statusText}\n${errorText}`
        );
      }
    } catch (error) {
      // If an error occurs during the request, display error message
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
