# Add comrades
INSERT INTO comrades (name, username, password, description) VALUES (null, null, null, null);

# Add proxy creds
INSERT INTO proxy_credentials (type, protocol, host, port, username, password, description, options) VALUES (null, null, null, null, null, null, null, null);

# Add proxy comrades
INSERT INTO proxy_comrades (proxy_credential_id, comrade_id, bandwidth_limit_b, concurrency_threads_limit, rotate_strategy) VALUES (null, null, 1024, 1, 1);

# Get proxy usage statistic by period
select sum(upload_traffic_bytes)/1073741824 as upload_traffic_gb , sum(download_traffic_bytes)/1073741824 as download_traffic_gb, sum(total_traffic_bytes)/1073741824 as total_traffic_gb from statistics where created_at>="" and created_at<"" and proxy_comrade_limit_id=;
