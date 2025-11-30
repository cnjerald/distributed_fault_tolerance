const API_BASE = "http://localhost:5000/api/student";

$(document).ready(function () {
    // require user to be logged
    const user = JSON.parse(localStorage.getItem("currentUser"));
    if (!user || !user.username) {
        alert("You must be logged in to view this page.");
        window.location.href = "/";
        return;
    }

    // initial load
    loadAvailableClasses();
    loadMyEnlistedClasses();

    $("#enlist_btn").click(enlistInClass);
});

// --------------------------
// 1. LOAD AVAILABLE SUBJECTS
// --------------------------
function loadAvailableClasses() {
    $.get(`${API_BASE}/subjects`)
        .done(function (res) {
            const table = $("#available_classes tbody");
            table.empty();

            // defensive: ensure res.subjects exists
            const subs = Array.isArray(res.subjects) ? res.subjects : [];
            subs.forEach(sub => {
                table.append(`
                    <tr>
                        <td>${sub.id}</td>
                        <td>${sub.course || sub.course_code}</td>
                        <td>${sub.units}</td>
                        <td>${sub.current_enrollees}/${sub.max_enrollees}</td>
                        <td><button onclick="selectClass('${sub.course || sub.course_code}')">Select</button></td>
                    </tr>
                `);
            });
        })
        .fail(function (xhr) {
            console.error("Failed to load available classes:", xhr);
            alert("Failed to load available classes. See console for details.");
        });
}

function selectClass(course) {
    $("#selected_course").val(course);
}

// ------------------------------------------
// 2. ENLIST IN A CLASS
// ------------------------------------------
function enlistInClass() {
    const course = $("#selected_course").val();
    const user = JSON.parse(localStorage.getItem("currentUser"));

    if (!course) {
        alert("Please select a course first.");
        return;
    }
    if (!user || !user.username) {
        alert("You are not logged in.");
        return;
    }

    const payload = { username: user.username, course };
    console.log("Enlist payload:", payload);

    $.ajax({
        url: `${API_BASE}/enlist`,
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function (res) {
            console.log("Enlist response:", res);
            alert(res.message || "Enlisted successfully!");
            // refresh both lists
            loadMyEnlistedClasses();
            loadAvailableClasses();
        },
        error: function (xhr, status, err) {
            console.error("Enlist failed:", status, err, xhr.responseText);
            let msg = "Failed to enlist.";
            if (xhr.responseJSON && xhr.responseJSON.error) msg += "\n" + xhr.responseJSON.error;
            alert(msg);
        }
    });
}

// ------------------------------------------
// 3. LOAD MY ENLISTED CLASSES + GRADES
// ------------------------------------------
function loadMyEnlistedClasses() {
    const user = JSON.parse(localStorage.getItem("currentUser"));
    if (!user || !user.username) {
        console.warn("No currentUser for loadMyEnlistedClasses");
        return;
    }

    const url = `${API_BASE}/records?username=${encodeURIComponent(user.username)}`;
    console.log("Loading records from:", url);

    $.get(url)
        .done(function (res) {
            const table = $("#my_classes tbody");
            table.empty();

            const records = Array.isArray(res.records) ? res.records : [];
            records.forEach(r => {
                table.append(`
                    <tr>
                        <td>${r.course}</td>
                        <td>${(r.grade !== null && r.grade >= 0) ? r.grade : "N/A"}</td>
                    </tr>
                `);
            });
        })
        .fail(function (xhr) {
            console.error("Failed to load my records:", xhr);
            alert("Failed to load your enrolled classes. See console.");
        });
}
