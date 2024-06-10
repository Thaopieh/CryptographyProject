
  document.getElementById("CreateCertificate").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/createcert";
  });
  document.getElementById("CreateRequestCertificate").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/CreateRequestCertificate";
  });
  document.getElementById("Createkey").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/Createkey";
  });
  document.getElementById("IssueQualificate").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/issue";
  });

  document.addEventListener("DOMContentLoaded", function () {
    // Lắng nghe sự kiện click vào nút "Logout"
    document.getElementById("logout").addEventListener("click", function () {
        // Gửi yêu cầu đăng xuất đến máy chủ
        fetch("authen/logout", {
            method: "GET"
        })
        .then(response => {
            // Kiểm tra phản hồi từ máy chủ
            if (response.ok) {
                // Đăng xuất thành công, chuyển hướng người dùng đến trang đăng nhập
                window.location.href = "/home";
            } else {
                // Xảy ra lỗi khi đăng xuất
                console.error("Failed to logout");
            }
        })
        .catch(error => {
            // Xảy ra lỗi khi gửi yêu cầu đến máy chủ
            console.error("Error:", error);
        });
    });
});
