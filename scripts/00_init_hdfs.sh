#!/bin/bash

echo "Đang tạo các thư mục trên HDFS..."
docker exec namenode hdfs dfs -mkdir -p /data/raw
docker exec namenode hdfs dfs -mkdir -p /data/processed
docker exec namenode hdfs dfs -mkdir -p /models

echo "Đang upload dữ liệu ban đầu lên HDFS..."
# Dữ liệu được mount vào namenode hoặc datanode? docker-compose.yml chỉ mount data vào spark.
# Do đó, ta sẽ copy từ máy host vào namenode, rồi đẩy lên HDFS.
docker cp ./data/raw/events.csv namenode:/tmp/events.csv
docker exec namenode hdfs dfs -put -f /tmp/events.csv /data/raw/events.csv
docker exec namenode rm /tmp/events.csv

echo "Hoàn tất upload dữ liệu ban đầu lên HDFS."
docker exec namenode hdfs dfs -ls /data/raw
