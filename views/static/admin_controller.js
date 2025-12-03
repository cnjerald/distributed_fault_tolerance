$(document).ready(function () {

    

    // ---------------- Logout ----------------
    $("#logout").click(function () {
        localStorage.removeItem("currentUser");  // clear user info
        alert("Logged out successfully");
        window.location.href = "/"; // redirect to main login page
    });

    // ---------------- Existing user management logic ----------------
    // Use environment variable if set (inside Docker), fallback to localhost for host browser
    const API_BASE = "http://localhost:5000/api/admin";


    // Simple authorization check
    const currentUser = JSON.parse(localStorage.getItem("currentUser"));
    if (!currentUser || currentUser.type !== "ADMIN") {
        alert("You are not authorized to view this page!");
        window.location.href = "/"; // redirect to login
        return;
    }

    function loadUsers() {
        $.ajax({
            url: `${API_BASE}/users`,
            method: "GET",
            success: function(res) {
                const tbody = $("#users_table tbody");
                tbody.empty();
                res.users.forEach(user => {
                    const row = $(`
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.username}</td>
                            <td>${user.type}</td>
                            <td>
                                <button class="delete_user" data-username="${user.username}">Delete</button>
                                <select class="update_type" data-username="${user.username}">
                                    <option value="STUDENT" ${user.type === 'STUDENT' ? 'selected' : ''}>STUDENT</option>
                                    <option value="TEACHER" ${user.type === 'TEACHER' ? 'selected' : ''}>TEACHER</option>
                                    <option value="ADMIN" ${user.type === 'ADMIN' ? 'selected' : ''}>ADMIN</option>
                                </select>
                                <button class="update_user" data-username="${user.username}">Update</button>
                            </td>
                        </tr>
                    `);
                    tbody.append(row);
                });
            },
            error: function(err) {
                console.error("Failed to load users:", err);
            }
        });
    }

    loadUsers();

    $("#create_user").click(function () {
        const username = $("#new_username").val();
        const type = $("#new_type").val();

        if (!username) {
            alert("Username cannot be empty");
            return;
        }

        $.ajax({
            url: `${API_BASE}/users`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({username, type}),
            success: function(res) {
                alert("User created successfully");
                $("#new_username").val("");
                loadUsers();
            },
            error: function(err) {
                console.error("Failed to create user:", err);
                alert("Failed to create user");
            }
        });
    });

    $(document).on("click", ".delete_user", function () {
        const username = $(this).data("username");
        if (!confirm(`Delete user ${username}?`)) return;

        $.ajax({
            url: `${API_BASE}/users/${username}`,
            method: "DELETE",
            success: function(res) {
                alert("User deleted");
                loadUsers();
            },
            error: function(err) {
                console.error("Failed to delete user:", err);
                alert("Failed to delete user");
            }
        });
    });

    $(document).on("click", ".update_user", function () {
        const username = $(this).data("username");
        const newType = $(this).siblings(".update_type").val();

        $.ajax({
            url: `${API_BASE}/users/${username}`,
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify({type: newType}),
            success: function(res) {
                alert("User updated");
                loadUsers();
            },
            error: function(err) {
                console.error("Failed to update user:", err);
                alert("Failed to update user");
            }
        });
    });
    loadSubjects();

    $("#create_subject").click(function () {
        const course_code = $("#course_code").val();
        const units = $("#units").val();
        const max_enrollees = $("#max_enrollees").val();

        const currentUser = JSON.parse(localStorage.getItem("currentUser")); // parse back
        const added_by = currentUser?.username; // get the username

        if (!added_by) {
            alert("You are not logged in. Cannot create subject.");
            return;
        }

        // Simple validation
        if (!course_code || !units || !max_enrollees) {
            alert("Please fill all fields before creating a subject.");
            return;
        }

        $.ajax({
            url: `${API_BASE}/subjects`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ course_code, units, max_enrollees, added_by }),
            success: function (res) {
                if (res.message) {
                    alert(res.message);
                    loadSubjects(); // reload the table
                } else if (res.error) {
                    alert("Error: " + res.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Failed to create subject:", status, error, xhr.responseText);
                let msg = "Failed to create subject.";
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    msg += "\n" + xhr.responseJSON.error;
                }
                alert(msg);
            }
        });
    });

    


    $.get(`${API_BASE}/subjects`, function (res) {
        const tbody = $("#subjects_table tbody");
        tbody.empty();

        res.subjects.forEach(r => {
            const row = $(`
                <tr>
                    <td>${r.id}</td>
                    <td>${r.course_code}</td>
                    <td>${r.units}</td>
                    <td>${r.added_by}</td>
                    <td>${r.current_enrollees}</td>
                    <td>${r.max_enrollees}</td>
                    <td><button class="delete-subject" data-id="${r.id}">Delete</button></td>
                </tr>
            `);
            tbody.append(row);
        });
    });

    function deleteSubject(id) {
        if (!confirm("Are you sure you want to delete this subject?")) return;

        $.ajax({
            url: `${API_BASE}/subjects/${id}`,
            method: "DELETE",
            success: function(res) {
                if (res.message) {
                    alert(res.message);
                    loadSubjects();
                } else if (res.error) {
                    alert("Error: " + res.error);
                }
            },
            error: function(xhr, status, error) {
                console.error("Failed to delete subject:", status, error, xhr.responseText);
                let msg = "Failed to delete subject.";
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    msg += "\n" + xhr.responseJSON.error;
                }
                alert(msg);
            }
        });
    }

    function loadSubjects() {
        $.get(`${API_BASE}/subjects`, function (res) {
            const tbody = $("#subjects_table tbody");
            tbody.empty();

            res.subjects.forEach(r => {
                const row = $(`
                    <tr>
                        <td>${r.id}</td>
                        <td>${r.course_code}</td>
                        <td>${r.units}</td>
                        <td>${r.added_by}</td>
                        <td>${r.current_enrollees}</td>
                        <td>${r.max_enrollees}</td>
                        <td><button class="delete-subject" data-id="${r.id}">Delete</button></td>
                    </tr>
                `);
                tbody.append(row);
            });
        });
    }

    
    $(document).on("click", ".delete-subject", function() {
        const id = $(this).data("id");
        deleteSubject(id);
    });

    // Load students and subjects into dropdowns
    function loadRecordDropdowns() {
        // Load students
        $.get(`${API_BASE}/users`, function(res) {
            const studentDropdown = $("#record_student_username");
            studentDropdown.empty();
            res.users
                .filter(u => u.type === "STUDENT")
                .forEach(u => studentDropdown.append(`<option value="${u.username}">${u.username}</option>`));
        });

        // Load subjects
        $.get(`${API_BASE}/subjects`, function(res) {
            const courseDropdown = $("#record_course");
            courseDropdown.empty();
            res.subjects.forEach(s => courseDropdown.append(`<option value="${s.course_code}">${s.course_code}</option>`));
        });
    }

    // Call on page load
    loadRecordDropdowns();
    loadRecords();

    // ---------------- Create Student Record ----------------
    $("#create_record").click(function() {
        const student_username = $("#record_student_username").val();
        const course = $("#record_course").val();
        const grade = parseInt($("#record_grade").val(), 10);

        if (!student_username || !course) {
            alert("Select a student and a course.");
            return;
        }

        $.ajax({
            url: `${API_BASE}/student_records`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ student_username, course, grade }),
            success: function(res) {
                if (res.message) {
                    alert(res.message);
                    loadRecords();
                    loadSubjects(); // refresh subjects table to show updated current_enrollees
                } else if (res.error) {
                    alert("Error: " + res.error);
                }
            },
            error: function(xhr, status, error) {
                console.error("Failed to add record:", status, error, xhr.responseText);
                let msg = "Failed to add record.";
                if (xhr.responseJSON && xhr.responseJSON.error) msg += "\n" + xhr.responseJSON.error;
                alert(msg);
            }
        });
    });

    // ---------------- Delete Student Record ----------------
    function deleteRecord(id) {
        $.ajax({
            url: `${API_BASE}/student_records/${id}`,
            method: "DELETE",
            success: function(res) {
                alert(res.message);
                loadRecords();
                loadSubjects(); // refresh subjects table to decrement current_enrollees if needed
            },
            error: function(xhr, status, error) {
                console.error("Failed to delete record:", status, error, xhr.responseText);
                alert("Failed to delete record.");
            }
        });
    }

    // ---------------- Load Student Records ----------------
    function loadRecords() {
        $.get(`${API_BASE}/student_records`, function(res) {
            const tbody = $("#records_table tbody");
            tbody.empty();

            res.records.forEach(r => {
                tbody.append(`
                    <tr>
                        <td>${r.id}</td>
                        <td>${r.student_username}</td>
                        <td>${r.course}</td>
                        <td>${r.grade}</td>
                        <td><button onclick="deleteRecord(${r.id})">Delete</button></td>
                    </tr>
                `);
            });
        }).fail(function(xhr, status, error) {
            console.error("Failed to load records:", status, error, xhr.responseText);
            alert("Failed to load student records.");
        });
    }

    // --------------- update student record -----------------
     function loadRecordOptions() {
        $.get(`${API_BASE}/student_records`, function(res) {
            const select = $("#edit_record_id");
            select.empty();
            res.records.forEach(r => {
                select.append(`<option value="${r.id}">ID:${r.id} - ${r.student_username} (${r.course})</option>`);
            });
        });
    }

    // Call on page load and after adding/deleting records
    loadRecordOptions();

    // Update grade click
  $("#update_grade").click(function() {
    const record_val = $("#edit_record_id").val();
    const match = record_val.match(/^(\d+)/); // match number at start
    if (!match) {
        alert("Invalid record selected.");
        return;
    }
    const record_id = parseInt(match[1], 10);

    const new_grade = parseInt($("#edit_grade").val(), 10);

    if (!record_id || isNaN(new_grade)) {
        alert("Select a record and enter a valid grade.");
        return;
    }
    console.log(record_id);

    $.ajax({
        url: `${API_BASE}/student_records/${record_id}`,
        method: "PUT",
        contentType: "application/json",
        data: JSON.stringify({ grade: new_grade }),
        success: function(res) {
            if (res.message) {
                alert(res.message);
                loadRecords();       // refresh table
                loadRecordOptions(); // refresh dropdown
            } else if (res.error) {
                alert("Error: " + res.error);
            }
        },
        error: function(xhr, status, error) {
            console.error("Failed to update grade:", status, error, xhr);

            let msg = `Failed to update grade.\n`;
            msg += `Status: ${xhr.status} ${xhr.statusText}\n`;
            msg += `Error: ${error}\n`;

            // Include JSON error if available
            if (xhr.responseJSON && xhr.responseJSON.error) {
                msg += `Server Message: ${xhr.responseJSON.error}\n`;
            } else if (xhr.responseText) {
                msg += `Response Text: ${xhr.responseText}\n`;
            }

            alert(msg);
        }
    });
});







});
