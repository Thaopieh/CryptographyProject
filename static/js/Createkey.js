document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById(
    "student-id-and-qualification-code-form"
  );
  const modal = document.getElementById("myModal");
  const modalMessage = document.getElementById("modal-message");

  form.addEventListener("submit", async function (event) {
    event.preventDefault(); // Ngăn chặn hành động mặc định của nút submit

    const schoolName = document.getElementById("SchoolName").value; // Lấy giá trị của trường nhập liệu

    // Tạo một đối tượng FormData và thêm trường 'school_name' vào đó
    const formData = new FormData();
    formData.append("school_name", schoolName);

    try {
      // Tạo một yêu cầu HTTP POST đến máy chủ để tạo key
      const response = await fetch("/school/genkey", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const responseText = await response.json();
        modalMessage.innerText = responseText.error;
        modal.style.display = "block";
        return;
      }

      const blob = await response.blob();

      // Kiểm tra xem API File System Access có được hỗ trợ hay không
      if ("showSaveFilePicker" in window) {
        const options = {
          suggestedName: "school_keys.zip",
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
        alert("Create successful and file saved.");
      } else {
        // Fallback cho các trình duyệt không hỗ trợ API File System Access
        const downloadUrl = window.URL.createObjectURL(blob);
        const downloadLink = document.createElement("a");
        downloadLink.href = downloadUrl;
        downloadLink.download = "school_keys.zip";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        window.URL.revokeObjectURL(downloadUrl);
        alert(
          "Create successful. Your browser does not support saving to a specific folder, so the file has been downloaded."
        );
      }
    } catch (error) {
      modalMessage.innerText = `An error occurred: ${error.message}`;
      modal.style.display = "block";
    }
  });

  // Đóng modal khi người dùng nhấp vào nút đóng
  const closeBtn = document.getElementsByClassName("close")[0];
  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });

  // Đóng modal khi người dùng nhấp vào bất kỳ đâu bên ngoài modal
  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
});
