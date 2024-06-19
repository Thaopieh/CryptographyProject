document.getElementById("getqualificate").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/getqua";
  });
  document.getElementById("Getkey").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/GetSchool";
  });
  
  document.getElementById("verifykey").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/verifykey";
  });
  document.getElementById("verifycertificate").addEventListener("click", function () {
    // Sử dụng JavaScript để chuyển hướng tới trang signing.html
    window.location.href = "/verify";
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