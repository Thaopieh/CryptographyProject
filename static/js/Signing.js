document.addEventListener("DOMContentLoaded", function () {
  var popup = document.getElementById("popup-form");
  var openPopupButton = document.getElementById("signing-button");
  var closePopupButton = document.querySelector(".popup .close");

  openPopupButton.addEventListener("click", function () {
    popup.style.display = "flex";
  });

  closePopupButton.addEventListener("click", function () {
    popup.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target == popup) {
      popup.style.display = "none";
    }
  });

  // Form submission handler
  const form = document.getElementById("signing-form");
  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    var institution = document.getElementById("institution").value;
    var authority = document.getElementById("authority").value;
    var email = document.getElementById("email").value;
    var studentID = document.getElementById("school").value;
    var studentName = document.getElementById("studentname").value;
    var qualificationFile = document.getElementById("qualification").files[0];
    var privateKeyFile = document.getElementById("privatekey").files[0];
    const emptyFile = new File([""], "public.b64", { type: "text/plain" });

    const formData = new FormData();
    formData.append("school_name", institution);
    formData.append("auth_name", authority);
    formData.append("auth_email", email);
    formData.append("student_id", studentID);
    formData.append("student_name", studentName);
    formData.append("qualificate", qualificationFile);
    formData.append("privateKey", privateKeyFile);
    formData.append("public_key", emptyFile);
    formData.append("certificate", emptyFile);

    try {
      const response = await fetch(
        "http://localhost:5000/qualificate/issue_qualificate",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          "Network response was not ok: " + JSON.stringify(errorData)
        );
      }

      const blob = await response.blob();

      if ("showSaveFilePicker" in window) {
        const options = {
          suggestedName: "certificate_with_qr.pdf",
          types: [
            {
              description: "PDF file",
              accept: { "application/pdf": [".pdf"] },
            },
          ],
        };

        const fileHandle = await window.showSaveFilePicker(options);
        const writable = await fileHandle.createWritable();
        await writable.write(blob);
        await writable.close();
        alert("Certificate saved successfully.");
      } else {
        // Fallback for browsers that do not support the File System Access API
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = "certificate_with_qr.pdf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        alert("Certificate downloaded successfully.");
      }

      // Clear the form after successful submission
      form.reset();
    } catch (error) {
      console.error("There was a problem with the fetch operation:", error);
      alert("There was a problem with the fetch operation: " + error.message);
    }
  });
});
