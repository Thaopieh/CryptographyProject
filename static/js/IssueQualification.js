document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById(
    "student-id-and-qualification-code-form"
  );
  const modal = document.getElementById("myModal");
  const modalMessage = document.getElementById("modal-message");

  form.addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent default form submission

    // Get values from input fields
    const schoolName = localStorage.getItem("school_name"); // Lấy giá trị của school_name từ localStorage
    const studentID = document.getElementById("Mssv").value;
    const studentName = document.getElementById("Name").value;
    const pdfFile = document.getElementById("input-file").files[0];
    const privateKeyFile = document.getElementById("private-key-file").files[0];

    // Create a FormData object and add data to it
    const formData = new FormData();
    formData.append("school_name", schoolName);
    formData.append("student_id", studentID);
    formData.append("student_name", studentName);
    formData.append("qualificate", pdfFile);
    formData.append("private_key", privateKeyFile);

    try {
      const response = await fetch("/qualificate/issue_qualificate", {
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

      const blob = await response.blob();

      // Check if the File System Access API is supported
      if ("showSaveFilePicker" in window) {
        const options = {
          suggestedName: `${studentID}_${schoolName}_qualificate_with_signature.zip`,
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
        showModal("Certificate issued successfully and file saved.");
      } else {
        // Fallback for browsers that do not support the File System Access API
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `${schoolName}_certificate_with_signature.zip`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);
        showModal(
          "Certificate issued successfully. Your browser does not support saving to a specific folder, so the file has been downloaded."
        );
      }

      // Clear the form after successful submission
      form.reset();
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
