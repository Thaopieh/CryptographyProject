document
  .getElementById("student-id-and-qualification-code-form")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    const qualificationCode =
      document.getElementById("qualification-code").value;
    const qualificationFile =
      document.getElementById("qualification-file").files[0];
    const publicKeyFile = document.getElementById("public-key-file").files[0];
    const school_name = document.getElementById("school_name").value;

    if (
      !qualificationFile ||
      !publicKeyFile ||
      !school_name ||
      !qualificationCode
    ) {
      alert("Please provide all required fields.");
      return;
    }

    // Step 1: Verify public key
    var publicKeyFormData = new FormData();
    publicKeyFormData.append("public_key", publicKeyFile);
    publicKeyFormData.append("school_name", school_name);

    fetch("http://localhost:5000/school/verify_public_key", {
      method: "POST",
      body: publicKeyFormData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Step 2: Verify qualification
          var formData = new FormData();
          formData.append("qualificate_id", qualificationCode);
          formData.append("qualificate", qualificationFile);
          formData.append("public_key", publicKeyFile);

          return fetch("http://localhost:5000/qualificate/verify_qualificate", {
            method: "POST",
            body: formData,
          });
        } else {
          throw new Error("Public key verification failed");
        }
      })
      .then((response) => response.json())
      .then((data) => {
        const modal = document.getElementById("myModal");
        const modalMessage = document.getElementById("modal-message");
        const closeButton = document.getElementsByClassName("close")[0];

        if (data.valid_pdf) {
          modalMessage.textContent = "Văn bằng này hợp lệ";
        } else {
          modalMessage.textContent = "Văn bằng này không hợp lệ";
        }

        modal.style.display = "block";

        closeButton.onclick = function () {
          modal.style.display = "none";
        };

        window.onclick = function (event) {
          if (event.target == modal) {
            modal.style.display = "none";
          }
        };
      })
      .catch((error) => {
        alert(`Error: ${error.message}`);
      });
  });
