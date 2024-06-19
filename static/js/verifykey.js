document.getElementById("student-id-and-qualification-code-form").addEventListener("submit", function (event) {
    event.preventDefault();

    const certificate = document.getElementById("qualification-file").files[0];
    const publicKeyFile = document.getElementById("public-key-file").files[0];

    if (!publicKeyFile || !certificate) {
        alert("Please provide all required fields.");
        return;
    }

    // Step 1: Verify public key
    var publicKeyFormData = new FormData();
    publicKeyFormData.append("public_key", publicKeyFile);
    publicKeyFormData.append("certificate", certificate);

    
    fetch("http://localhost:5000/school/verify_key_cert", {
        method: "POST",
        body: publicKeyFormData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Xác minh khóa công khai thành công, thực hiện các bước tiếp theo
            console.log(data.success);
            alert(data.success);
          } else {
            throw new Error(data.error || "Khóa công khai không khớp với chứng chỉ");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert(error.message || "Xác minh khóa công khai thất bại.");
        });
});
