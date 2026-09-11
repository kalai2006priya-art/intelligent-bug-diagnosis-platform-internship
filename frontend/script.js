// ===============================
// LOGIN
// ===============================

document
    .getElementById("loginForm")
    .addEventListener("submit", function(event) {

        event.preventDefault();

        const username =
            document.getElementById("username").value;

        const password =
            document.getElementById("password").value;

        if (username === "admin" && password === "admin123") {

            window.location.href = "dashboard.html";

        } else {

            const message =
                document.getElementById("loginMessage");

            message.style.color = "red";

            message.textContent =
                "Invalid username or password.";

        }

    });


// ===============================
// BUG SUBMISSION + FILE UPLOAD
// ===============================

const bugForm = document.getElementById("bugForm");

if (bugForm) {

    bugForm.addEventListener("submit", async function(event) {

        event.preventDefault();

        const title =
            document.getElementById("title").value.trim();

        const description =
            document.getElementById("description").value.trim();

        const stackTrace =
            document.getElementById("stackTrace").value.trim();

        const errorLogsElement =
            document.getElementById("errorLogs");

        const bugFile =
            document.getElementById("bugFile").files[0];

        const submitBtn =
            document.getElementById("submitBtn");

        const resultBox =
            document.getElementById("resultBox");

        const errorBox =
            document.getElementById("errorBox");


        // Hide old results
        resultBox.style.display = "none";
        errorBox.style.display = "none";


        // Loading
        submitBtn.disabled = true;
        submitBtn.innerText = "Analyzing...";


        try {

            // ===============================
            // FILE UPLOAD
            // ===============================

            if (bugFile) {

                const formData = new FormData();

                formData.append("file", bugFile);

                const uploadResponse =
                    await fetch(
                        "http://127.0.0.1:8000/bugs/upload",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                const uploadResult =
                    await uploadResponse.json();


                if (!uploadResponse.ok) {

                    throw new Error(
                        uploadResult.detail ||
                        "File upload failed."
                    );

                }


                // Put uploaded file content
                // into Error Logs box
                if (!errorLogsElement.value.trim()) {

                    errorLogsElement.value =
                        uploadResult.content || "";

                }

            }


            // ===============================
            // BUG DATA
            // ===============================

            const bugData = {

                title: title,

                description: description,

                stack_trace: stackTrace,

                error_logs:
                    errorLogsElement.value.trim()

            };


            // ===============================
            // SEND TO FASTAPI
            // ===============================

            const response =
                await fetch(
                    "http://127.0.0.1:8000/bugs",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(bugData)
                    }
                );


            const result =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    result.detail ||
                    "Bug submission failed."
                );

            }


            // ===============================
            // SHOW RESULT
            // ===============================

            resultBox.style.display = "block";


            // Bug ID
            document
                .getElementById("bugId")
                .innerText =
                    result.id ?? "-";


            // ===============================
            // TRIAGE RESULT
            // ===============================

            const triage =
                result.triage || {};


            document
                .getElementById("severity")
                .innerText =
                    triage.severity ?? "-";


            document
                .getElementById("priority")
                .innerText =
                    triage.priority ?? "-";


            document
                .getElementById("component")
                .innerText =
                    triage.affected_component ?? "-";


            document
                .getElementById("confidence")
                .innerText =
                    triage.confidence_score ?? "-";


            // ===============================
            // LOG ANALYSIS RESULT
            // ===============================

            const logAnalysis =
                result.log_analysis || {};


            document
                .getElementById("exceptionType")
                .innerText =
                    logAnalysis.exception_type ??
                    "Unknown";


            document
                .getElementById("errorMessage")
                .innerText =
                    logAnalysis.error_message ??
                    "Unable to determine";


            document
                .getElementById("failurePoint")
                .innerText =
                    logAnalysis.failure_point ??
                    "Unable to determine";


            document
                .getElementById("codePath")
                .innerText =
                    logAnalysis.affected_code_path ??
                    "Unable to determine";


            document
                .getElementById("logConfidence")
                .innerText =
                    logAnalysis.confidence_score ??
                    "-";


            // Reset form
            bugForm.reset();

        }


        catch (error) {

            console.error(
                "Error:",
                error
            );


            errorBox.style.display =
                "block";


            if (
                error.message.includes(
                    "Failed to fetch"
                )
            ) {

                errorBox.innerText =
                    "Cannot connect to FastAPI backend. Please check that the backend is running.";

            } else {

                errorBox.innerText =
                    error.message;

            }

        }


        // Restore button
        submitBtn.disabled = false;

        submitBtn.innerText =
            "Analyze Bug";

    });

}