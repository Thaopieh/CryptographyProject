document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById(
    "student-id-and-qualification-code-form"
  );
  const modal = document.getElementById("myModal");
  const modalMessage = document.getElementById("modal-message");

  form.addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form submission

    // Get the values from the input fields
    const schoolName = localStorage.getItem("school_name"); // Lấy giá trị của school_name từ localStorage
    const csrFile = document.getElementById("CSR-file").files[0];

    // Check if a CSR file is selected
    if (!csrFile) {
      showModal("Please select a CSR file.");
      return;
    }

    // Create a FormData object
    const formData = new FormData();
    formData.append("school_name", schoolName);
    formData.append("csr", csrFile);

    try {
      const response = await fetch("/school/get_certificate", {
        method: "POST",
        body: formData, // Send form data using FormData
      });

      if (!response.ok) {
        const errorText = await response.text();
        showModal(
          `Error: ${response.status} ${response.statusText}\n${errorText}`
        );
        return;
      }

      // Handle the successful response
      const blob = await response.blob();

      // Check if the browser supports the File System Access API
      if ("showSaveFilePicker" in window) {
        const options = {
          suggestedName: `${schoolName}_with_RootCA_certificate.zip`,
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
        showModal("File saved successfully.");
      } else {
        // Fallback for browsers that do not support the File System Access API
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${schoolName}_with_RootCA_certificate.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        showModal("File downloaded successfully.");
      }
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
