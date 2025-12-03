$(document).ready(function () {

    // ---------------- Logout ----------------
    $("#logout").click(function () {
        localStorage.removeItem("currentUser");
        alert("Logged out");
        window.location.href = "/";
    });

    // ---------------- Authorization ----------------
    const API_BASE = "http://localhost:5000/api/teacher";

    const currentUser = JSON.parse(localStorage.getItem("currentUser"));
    if (!currentUser || currentUser.type !== "TEACHER") {
        alert("You are not authorized to view this page!");
        window.location.href = "/";
        return;
    }

    // ---------------- Subjects Management ----------------
    function loadSubjects() {
        $.get(`${API_BASE}/subjects`, function (res) {
            const tbody = $("#subjects_table tbody");
            tbody.empty();

            res.subjects.forEach(s => {
                tbody.append(`
                    <tr>
                        <td>${s.id}</td>
                        <td>${s.course_code}</td>
                        <td>${s.units}</td>
                        <td>${s.added_by}</td>
                        <td>${s.current_enrollees}</td>
                        <td>${s.max_enrollees}</td>
                        <td><button class="delete-subject" data-id="${s.id}">Delete</button></td>
                    </tr>
                `);
            });
        });
    }

    loadSubjects();

    $("#create_subject").click(function () {
        const course_code = $("#course_code").val();
        const units = $("#units").val();
        const max_enrollees = $("#max_enrollees").val();
        const added_by = currentUser.username;

        if (!course_code || !units || !max_enrollees) {
            alert("Fill all fields");
            return;
        }

        $.ajax({
            url: `${API_BASE}/subjects`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ course_code, units, max_enrollees, added_by }),
            success: function (res) {
                alert(res.message);
                loadSubjects();
            },
            error: function (xhr) {
                console.error(xhr);
                alert("Failed to create subject");
            }
        });
    });

    $(document).on("click", ".delete-subject", function () {
        const id = $(this).data("id");

        if (!confirm("Delete subject?")) return;

        $.ajax({
            url: `${API_BASE}/subjects/${id}`,
            method: "DELETE",
            success: function (res) {
                alert(res.message);
                loadSubjects();
            },
            error: function (xhr) {
                alert("Failed to delete subject");
            }
        });
    });

    // ---------------- Student Records ----------------
    function loadRecordDropdowns() {
        // Load students
        $.get(`${API_BASE}/users`, function (res) {
            const dropdown = $("#record_student_username");
            dropdown.empty();
            res.students.forEach(u =>
                dropdown.append(`<option value="${u.username}">${u.username}</option>`)
            );
        });

        // Load subjects
        $.get(`${API_BASE}/subjects`, function (res) {
            const dropdown = $("#record_course");
            dropdown.empty();
            res.subjects.forEach(s =>
                dropdown.append(`<option value="${s.course_code}">${s.course_code}</option>`)
            );
        });
    }

    // On first load:
    loadRecordDropdowns();

    // After loading subjects, auto-trigger filter once
    setTimeout(() => {
        $("#record_course").trigger("change");
    }, 300);


    $("#create_record").click(function () {
        const student_username = $("#record_student_username").val();
        const course = $("#record_course").val();
        const grade = parseInt($("#record_grade").val(), 10);

        $.ajax({
            url: `${API_BASE}/student_records`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ student_username, course, grade }),
            success: function (res) {
                alert(res.message);
                loadRecords();
            },
            error: function (xhr) {
                alert("Failed to add record");
            }
        });
    });

    function deleteRecord(id) {
        $.ajax({
            url: `${API_BASE}/student_records/${id}`,
            method: "DELETE",
            success: function (res) {
                alert(res.message);
                loadRecords();
            },
            error: function () {
                alert("Failed to delete record");
            }
        });
    }

    function loadRecords() {
        $.get(`${API_BASE}/student_records`, function (res) {
            const tbody = $("#records_table tbody");
            tbody.empty();

            res.records.forEach(r => {
                tbody.append(`
                    <tr>
                        <td>${r.id}</td>
                        <td>${r.student_username}</td>
                        <td>${r.course}</td>
                        <td>${r.grade}</td>
                        <td><button class="delete-record" data-id="${r.id}">Delete</button></td>
                    </tr>
                `);
            });
        });
    }


    $(document).on("click", ".delete-record", function () {
        const id = $(this).data("id");
        deleteRecord(id);
    });


    loadRecords();

    // ---------------- Grade Update ----------------
    function loadRecordOptions() {
        $.get(`${API_BASE}/student_records`, function (res) {
            const select = $("#edit_record_id");
            select.empty();

            res.records.forEach(r => {
                select.append(`<option value="${r.id}">ID:${r.id} – ${r.student_username} (${r.course})</option>`);
            });
        });
    }

    loadRecordOptions();

    $("#update_grade").click(function () {
        const id = parseInt($("#edit_record_id").val());
        const grade = parseInt($("#edit_grade").val());

        $.ajax({
            url: `${API_BASE}/student_records/${id}`,
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify({ grade }),
            success: function (res) {
                alert(res.message);
                loadRecords();
                loadRecordOptions();
            },
            error: function (xhr) {
                alert("Failed to update grade");
            }
        });
    });

    // When course is selected, reload eligible students
    $("#record_course").change(function () {
        const course = $(this).val();
        loadStudentsForCourse(course);
    });

function loadStudentsForCourse(course) {
    if (!course) return;

    // 1. Get enrolled students for that course
    $.get(`${API_BASE}/student_records`, function(res) {
        const enrolled = res.records
            .filter(r => r.course === course)
            .map(r => r.student_username);

        // 2. Get all STUDENTS from teacher service (already filtered to STUDENT only)
        $.get(`${API_BASE}/users`, function(usersRes) {
            const dropdown = $("#record_student_username");
            dropdown.empty();

            usersRes.students
                .filter(u => !enrolled.includes(u.username))  // exclude already enrolled
                .forEach(u => {
                    dropdown.append(
                        `<option value="${u.username}">${u.username}</option>`
                    );
                });
        });
    });
}





});
