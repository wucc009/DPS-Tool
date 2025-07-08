<?php
$unique_id = uniqid();

$upload_dir = "uploads/" . $unique_id;
$result_dir = "results/" . $unique_id;

mkdir($upload_dir, 0777, true);
mkdir($result_dir, 0777, true);

$expression_matrix = $_FILES['expression_matrix'];
$sample_info = $_FILES['sample_info'];

$negative_class = $_POST['negative_class'];
$positive_class = $_POST['positive_class'];
$reversion_threshold = $_POST['reversion_threshold'];
$deduplicate = $_POST['deduplicate'];
$sample_info_category = isset($_POST['sample_info_category']) ? $_POST['sample_info_category'] : null;
$sample_category = isset($_POST['sample_category']) ? $_POST['sample_category'] : null;
$data_type = isset($_POST['data_type']) ? $_POST['data_type'] : null;

move_uploaded_file($expression_matrix['tmp_name'], $upload_dir . '/expression_matrix.csv');
move_uploaded_file($sample_info['tmp_name'], $upload_dir . '/sample_info.csv');

$gene_set_file = null;
if (isset($_FILES['gene_set_file']) && is_uploaded_file($_FILES['gene_set_file']['tmp_name']) && $_FILES['gene_set_file']['size'] > 0) {
    $gene_set_file = $_FILES['gene_set_file'];
    move_uploaded_file($gene_set_file['tmp_name'], $upload_dir . '/gene_set.csv');
}

$command = [
    '/home/hj/miniconda3/envs/py310/bin/python', './dps_tool/DPS-Tool.py',
    '--expression_matrix', $upload_dir . '/expression_matrix.csv',
    '--sample_info', $upload_dir . '/sample_info.csv',
    '--negative_class', $negative_class,
    '--positive_class', $positive_class,
    '--output_dir', $result_dir,
    '--reversion_threshold', $reversion_threshold,
    '--deduplicate', $deduplicate
];

if ($gene_set_file) {
    $command[] = '--gene_set_file';
    $command[] = $upload_dir . '/gene_set.csv';
}
if ($sample_info_category) {
    $command[] = '--sample_info_category';
    $command[] = $sample_info_category;
}
if ($sample_category) {
    $command[] = '--sample_category';
    $command[] = $sample_category;
}
if ($data_type) {
    $command[] = '--data_type';
    $command[] = $data_type;
}

$task_id = $unique_id; 
file_put_contents("task_status/{$task_id}.status", "processing");

$background_command = implode(' ', $command) . " > /dev/null 2>&1 &";
shell_exec($background_command);

header('Content-Type: application/json');
echo json_encode(['task_id' => $task_id]);
?>