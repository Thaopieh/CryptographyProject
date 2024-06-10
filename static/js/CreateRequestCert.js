document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById(
    "student-id-and-qualification-code-form"
  );
  const modal = document.getElementById("myModal");
  const modalMessage = document.getElementById("modal-message");

  form.addEventListener("submit", async function (event) {
    event.preventDefault(); // Ngăn chặn gửi form theo cách thông thường

    // Lấy giá trị từ các trường nhập liệu
    const schoolName = localStorage.getItem("school_name"); // Lấy giá trị của school_name từ localStorage
    const authName = document.getElementById("Name").value;
    const authEmail = document.getElementById("email").value;
    const country = document.getElementById("country").value;
    const state = document.getElementById("Province").value;
    const locality = document.getElementById("City").value;
    const orgUnit = document.getElementById("Organization").value;
    const privateKeyFile = document.getElementById("private-key-file").files[0];

    // Kiểm tra xem tất cả các trường nhập liệu đã được điền chưa
    if (
      !schoolName ||
      !authName ||
      !authEmail ||
      !country ||
      !state ||
      !locality ||
      !orgUnit ||
      !privateKeyFile
    ) {
      showModal("Please fill out all fields.");
      return;
    }

    // Tạo một đối tượng FormData
    const formData = new FormData();
    formData.append("school_name", schoolName);
    formData.append("auth_name", authName);
    formData.append("auth_email", authEmail);
    formData.append("C", country);
    formData.append("ST", state);
    formData.append("L", locality);
    formData.append("OU", orgUnit);
    formData.append("private_key", privateKeyFile);

    try {
      const response = await fetch("/school/require_cert", {
        method: "POST",
        body: formData, // Gửi dữ liệu form sử dụng FormData
      });

      if (!response.ok) {
        const errorText = await response.text();
        showModal(
          `Error: ${response.status} ${response.statusText}\n${errorText}`
        );
        return;
      }

      // Nếu thành công, hiển thị thông báo và tải tệp CSR xuống
      const csrBlob = await response.blob();
      if ("showSaveFilePicker" in window) {
        const options = {
          suggestedName: `${schoolName}.csr`,
          types: [
            {
              description: "CSR file",
              accept: { "application/x-pem-file": [".csr"] },
            },
          ],
        };
        const fileHandle = await window.showSaveFilePicker(options);
        const writable = await fileHandle.createWritable();
        await writable.write(csrBlob);
        await writable.close();
        showModal("CSR created and saved successfully.");
      } else {
        // Fallback for browsers that do not support File System Access API
        const downloadLink = document.createElement("a");
        downloadLink.href = URL.createObjectURL(csrBlob);
        downloadLink.download = `${schoolName}.csr`;
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        showModal("CSR created successfully.");
      }

      // Clear form after successful submission
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
