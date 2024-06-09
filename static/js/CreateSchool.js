document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById(
    "student-id-and-qualification-code-form"
  );

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const schoolName = document.getElementById("schoolname").value;

    if (!schoolName) {
      alert("School name cannot be empty.");
      return;
    }

    const formData = new FormData();
    formData.append("school_name", schoolName);

    try {
      const response = await fetch(
        "http://localhost:5000/school/create_school",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        alert(`Error: ${response.status} ${response.statusText}\n${errorText}`);
        return;
      }

      const data = await response.json();
      alert(data.success || data.error);
    } catch (error) {
      alert("An error occurred: " + error.message);
    }
  });
});
