<?php
$task_id = $_GET['task_id'];
$result_dir = "results/" . $task_id;

$DP_score_with_sample_information = file_exists($result_dir . "/DP_score_with_sample_information.pdf");
?>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DPS-Tool - Results</title>
    <link rel="stylesheet" href="./css/bootstrap.min.css" />
    <link
      rel="stylesheet"
      href="./css/fontawesome-free-5.15.3-web/css/all.min.css"
    />
    <style>
      body {
        background-color: #f8f9fa;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
      }

      .navbar {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        background-color: #2c3e50;
      }

      .navbar-brand {
        font-weight: 600;
      }

      .jumbotron {
        background-color: #e9ecef;
        border-radius: 10px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
      }

      .feature-icon {
        font-size: 2.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
      }

      .card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        overflow: hidden;
      }

      .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
      }

      .card-body {
        padding: 1.5rem;
      }

      .card-title {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e9ecef;
      }

      .accordion .card-header {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 1rem;
      }

      footer {
        background-color: #343a40;
        color: white;
        padding: 2rem 0;
      }

      .carousel-item img {
        height: 400px;
        object-fit: cover;
        border-radius: 10px;
      }

      .section-title {
        position: relative;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        font-weight: 600;
        color: #2c3e50;
      }

      .section-title::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 3px;
        background-color: #2c3e50;
      }

      .carousel-control-prev-icon,
      .carousel-control-next-icon {
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 50%;
        padding: 20px;
      }

      .rolling-line {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2rem 0;
      }

      .rolling-line hr {
        flex-grow: 1;
        margin: 0 10px;
        border-color: #2c3e50;
      }

      .rolling-square {
        position: absolute;
        width: 20px;
        height: 20px;
        background-color: #888;
        top: -22.5px;
        animation: roll 15s linear infinite, rotate 2s linear infinite;
      }

      @keyframes roll {
        0% {
          left: -20px;
        }
        50% {
          left: 100%;
        }
        100% {
          left: -20px;
        }
      }

      @keyframes rotate {
        0% {
          transform: rotate(0deg);
        }
        100% {
          transform: rotate(360deg);
        }
      }

      .btn-custom {
        background-color: #2c3e50;
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 0.25rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }

      .btn-custom:hover {
        background-color: #3a4e60;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        text-decoration: none;
      }

      .btn-custom .fas {
        margin-right: 0.5rem;
      }

      .img-container {
            width: 100%;
            height: 177.89px;
            background-color:rgb(255, 255, 255);
            border-radius: 8px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }

      .img-fluid {
          max-width: 100%;
          max-height: 100%;
          object-fit: contain;
          border-radius: 8px;
          transition: transform 0.3s ease;
          cursor: pointer;
      }

      .img-fluid:hover {
        transform: scale(1.02);
      }

      .card-body {
        padding: 1.5rem;
      }

      .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #2c3e50;
      }

      .card-text {
        color: #555;
        line-height: 1.6;
      }

      .btn-group {
        margin-bottom: 1rem;
      }

      .img-loading {
        opacity: 0;
        transition: opacity 0.5s ease;
      }

      .img-loading.loaded {
        opacity: 1;
      }

      .btn-group {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
      }

      .btn-group .btn {
        margin: 0 0.25rem;
      }

      .card {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
      }

      .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
      }

      .btn-group .btn {
        margin: 0 0.25rem;
      }

      .img-loading {
        opacity: 0;
        transition: opacity 0.5s ease;
      }

      .img-loading.loaded {
        opacity: 1;
      }

      .card-divider {
        height: 1px;
        background-color: #e9ecef;
        margin: 1rem 0;
      }

      .modal-img {
        max-width: 100%;
        max-height: 80vh;
        object-fit: contain;
      }
    </style>
  </head>
  <body>
    <nav
      class="navbar navbar-expand-lg navbar-dark"
      style="background-color: #2c3e50"
    >
      <div class="container">
        <a class="navbar-brand" href="index.html">
          <i class="fas fa-chart-line mr-2"></i>DPS-Tool
        </a>
        <button
          class="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ml-auto">
            <li class="nav-item">
              <a class="nav-link" href="index.html">Home</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="run.html">Run</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="example.html">Example</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="help.html">Help</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container mt-5">
      <h1 class="section-title" style="text-align: center">Analysis Results</h1>

      <div class="row">
        <div class="col-md-6">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">TOP10 Gene Pairs Bar Chart</h5>
              <div class="img-container">
              <img 
                src="<?php echo $result_dir . '/TOP10_gene_pairs_bar_chart.png'; ?>" 
                class="img-fluid img-loading" 
                alt="TOP10 gene pairs bar chart" 
                onload="this.classList.add('loaded')"
                data-toggle="modal" 
                data-target="#imageModal" 
                data-img-src="<?php echo $result_dir . '/TOP10_gene_pairs_bar_chart.png'; ?>"
                />
                </div>
              <div class="card-divider"></div>
              <div class="btn-group">
                <a 
                  href="<?php echo $result_dir . '/Gene_pairs_table.csv'; ?>" 
                  class="btn btn-custom"
                >
                  <i class="fas fa-download"></i> Gene Pairs Table
                </a>
                <a 
                  href="<?php echo $result_dir . '/TOP10_gene_pairs_bar_chart.pdf'; ?>" 
                  class="btn btn-custom" 
                  download
                >
                  <i class="fas fa-download"></i> TOP10 Gene Pairs Bar Chart
                </a>
              </div>
            </div>
          </div>
        </div>

        <div class="col-md-6">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">DP_Score Bar Chart</h5>
              <div class="img-container">
              <img 
                src="<?php echo $result_dir . '/DP_score_bar_chart.png'; ?>" 
                class="img-fluid img-loading" 
                alt="DP_score bar chart" 
                onload="this.classList.add('loaded')"
                data-toggle="modal" 
                data-target="#imageModal" 
                data-img-src="<?php echo $result_dir . '/DP_score_bar_chart.png'; ?>"
              /></div>
              <div class="card-divider"></div>
              <div class="btn-group">
                <a href="<?php echo $result_dir . '/DP_score_table.csv'; ?>" class="btn btn-custom">
                  <i class="fas fa-download"></i> DP_Score Table
                </a>
                <a 
                  href="<?php echo $result_dir . '/DP_score_bar_chart.pdf'; ?>" 
                  class="btn btn-custom" 
                  download
                >
                  <i class="fas fa-download"></i> DP_Score Bar Chart
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-md-6">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">DP_Score Boxplot</h5>
              <div class="img-container">
              <img 
                src="<?php echo $result_dir . '/DP_score_boxplot.png'; ?>" 
                class="img-fluid img-loading" 
                alt="DP_score boxplot" 
                onload="this.classList.add('loaded')"
                data-toggle="modal" 
                data-target="#imageModal" 
                data-img-src="<?php echo $result_dir . '/DP_score_boxplot.png'; ?>"
              /></div>
              <div class="card-divider"></div>
              <div class="btn-group">
                <a 
                  href="<?php echo $result_dir . '/DP_score_boxplot.pdf'; ?>" 
                  class="btn btn-custom" 
                  download
                >
                  <i class="fas fa-download"></i> DP_Score Boxplot
                </a>
              </div>
            </div>
          </div>
        </div>

        <?php if ($DP_score_with_sample_information): ?>
        <div class="col-md-6">
          <div class="card mb-4">
            <div class="card-body">
              <h5 class="card-title">DP_Score With Sample Information Plot</h5>
              <div class="img-container">
              <img 
                src="<?php echo $result_dir . '/DP_score_with_sample_information.png'; ?>" 
                class="img-fluid img-loading" 
                alt="DP score with sample information plot" 
                onload="this.classList.add('loaded')"
                data-toggle="modal" 
                data-target="#imageModal" 
                data-img-src="<?php echo $result_dir . '/DP_score_with_sample_information.png'; ?>"
              /></div>
              <div class="card-divider"></div>
              <div class="btn-group">
                <a 
                  href="<?php echo $result_dir . '/DP_score_with_sample_information.pdf'; ?>" 
                  class="btn btn-custom" 
                  download
                >
                  <i class="fas fa-download"></i> DP_Score With Sample Information Plot
                </a>
              </div>
            </div>
          </div>
        </div>
        <?php endif; ?>
      </div>
    </div>

    <div
      class="modal fade"
      id="imageModal"
      tabindex="-1"
      role="dialog"
      aria-labelledby="imageModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="imageModalLabel">Image Preview</h5>
            <button
              type="button"
              class="close"
              data-dismiss="modal"
              aria-label="Close"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body text-center">
            <img src="" class="modal-img" id="modalImage" alt="Preview Image" />
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-light text-center py-4 mt-5">
      <div class="container">
        <div class="rolling-line">
          <hr />
          <div class="rolling-square"></div>
        </div>
        <p class="text-muted">© 2025 DPS-Tool. All rights reserved.</p>
      </div>
    </footer>

    <script src="./js/jquery-3.5.1.slim.min.js"></script>
    <script src="./js/bootstrap.bundle.min.js"></script>
    <script src="./js/popper.min.js"></script>
    <script>
      $(document).ready(function () {
        $('[data-toggle="modal"]').on("click", function () {
          const imgSrc = $(this).data("img-src");
          $("#modalImage").attr("src", imgSrc);
          $("#imageModal").modal("show");
        });

        $(".img-loading").each(function () {
          $(this).on("load", function () {
            $(this).addClass("loaded");
          });
        });
      });
    </script>
  </body>
</html>
