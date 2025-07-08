<?php
$task_id = $_GET['task_id'];
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DPS-Tool - Processing</title>
    <link rel="stylesheet" href="./css/bootstrap.min.css" />
    <link
      rel="stylesheet"
      href="./css/fontawesome-free-5.15.3-web/css/all.min.css"
    />
    <style>
        .waiting-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 70vh;
            padding: 2rem;
        }
        .waiting-text {
            text-align: center;
            font-size: 1.2rem;
            color: #495057;
            margin: 2rem 0;
        }
        .loading-circle {
            width: 80px;
            height: 80px;
            border: 5px solid #0aadd6d5;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 2s linear infinite;
            margin: 2rem auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="waiting-container">
        <div class="loading-circle"></div>
        <div class="waiting-text">
            <p>It will take 3 to 7 minutes to get the results. Please wait patiently...</p>
        </div>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="./js/bootstrap.bundle.min.js"></script>
    <script src="./js/popper.min.js"></script>
    <script>
        var taskId = "<?php echo $task_id; ?>";

        function checkTaskStatus() {
            $.ajax({
                url: "check_status.php?task_id=" + taskId,
                success: function (data) {
                    if (data === "completed") {
                        window.location.href = "result.php?task_id=" + taskId;
                    } else if (data.startsWith("failed")) {
                        alert("The task execution failed!");
                        window.location.href = "error.html";
                    }
                }
            });
        }

        setInterval(checkTaskStatus, 5000);
    </script>
    </body>
</html>