#Replace your API key and Atlas Task ID

###prometheus configuration###

  - job_name: 'ripe-atlas-ping'
    scrape_interval: 60s
    metrics_path: /
    params:
      module: [PING]
    target_groups:
      - targets:
          - 4492348 <- TASK ID
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
        replacement: ${1}
      - source_labels: [__param_target]
        regex: (.*)
        target_label: instance
        replacement: ${1}
      - source_labels: []
        regex: .*
        target_label: __address__
        replacement: 127.0.0.1:9001  # Blackbox exporter.
