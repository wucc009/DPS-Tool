<?php
$task_id = $_GET['task_id'];
$status_file = "task_status/{$task_id}.status";

if (file_exists($status_file)) {
    $status = file_get_contents($status_file);
    echo $status;
} else {
    echo "processing";
}
?>