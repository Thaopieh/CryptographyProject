document.getElementById('student-id-and-qualification-code-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const qualificationCode = document.getElementById('qualification-code').value;
    const qualificationFile = document.getElementById('qualification-file').files[0];
    const publicKeyFile = document.getElementById('public-key-file').files[0];

    if (!qualificationFile || !publicKeyFile) {
        alert('Please select both qualification and public key files.');
        return;
    }

    const formData = new FormData();
    formData.append('qualificate_id', qualificationCode);
    formData.append('qualificate', qualificationFile);
    formData.append('public_key', publicKeyFile);

    fetch('http://localhost:5000/qualificate/verify_qualificate', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const modal = document.getElementById('myModal');
        const modalMessage = document.getElementById('modal-message');
        const closeButton = document.getElementsByClassName('close')[0];

        if (data.valid_pdf) {
            modalMessage.textContent = 'Văn bằng này hợp lệ';
        } else {
            modalMessage.textContent = 'Văn bằng này không hợp lệ';
        }

        modal.style.display = 'block';

        closeButton.onclick = function() {
            modal.style.display = 'none';
        };

        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        };
    })
    .catch(error => {
        alert(`Error: ${error.message}`);
    });
});
