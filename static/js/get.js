document
  .getElementById("student-id-and-qualification-code-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const studentId = document.getElementById("student-id").value;
    const qualificationCode =
      document.getElementById("qualification-code").value;
    const schoolName = document.getElementById("schoolname").value;
    // Function to decode JWT token

    try {
      const response = await fetch(
        `http://localhost:5000/qualificate/get_qualificate?student_id=${studentId}&qualificate_id=${qualificationCode}&school_name=${encodeURIComponent(
          schoolName
        )}`,
        {
          method: "GET",
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error);
      }

      const blob = await response.blob();

      // Check if the browser supports the File System Access API
      if ("showSaveFilePicker" in window) {
        const options = {
          suggestedName: `${studentId}_qualificate_and_certificate.zip`,
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
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = `${studentId}_qualificate_and_certificate.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        alert("File downloaded successfully.");
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
  });
