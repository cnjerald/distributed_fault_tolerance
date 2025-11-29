// python -m http.server 3000

$(document).ready(function () {

    $("#login").click(function () {
        const data = {
            username: $("#username").val(),
            password: $("#password").val()
        };

        $.ajax({
            url: "http://localhost:5000/api/login",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function(res) {
                if (res.message === "Login OK") {
                    const type = res.user.type;
                    localStorage.setItem("currentUser", JSON.stringify(res.user));
                    // Redirect based on user type
                    if (type === "ADMIN") window.location.href = "admin.html";
                    else if (type === "TEACHER") window.location.href = "teacher.html";
                    else window.location.href = "student.html";
                } else {
                    alert("Invalid credentials");
                }
            }
        });
    });

});
