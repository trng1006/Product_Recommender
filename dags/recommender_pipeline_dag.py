"""
Airflow DAG điều phối toàn diện Pipeline Big Data cho Hệ Khuyến Nghị Sản Phẩm (HUIT)
Quy trình: 
  1. Kiểm tra sự sẵn sàng của dữ liệu thô trên HDFS (Sensor/Check)
  2. Kích hoạt Spark Job thực hiện ETL (Làm sạch & Chuyển đổi Parquet)
  3. Kích hoạt Spark SQL Job trích xuất Top 10 sản phẩm (Cold-Start fallback)
  4. Kích hoạt Spark MLlib huấn luyện mô hình ALS phân tán
  5. Xuất metadata và thông báo hoàn tất pipeline
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator

default_args = {
    'owner': 'HUIT_BigData_Team',
    'depends_on_past': False,
    'start_date': datetime(2026, 10, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    dag_id='product_recommender_bigdata_pipeline',
    default_args=default_args,
    description='Pipeline điều phối ETL và Huấn luyện mô hình ALS trên HDFS và Spark',
    schedule_interval='@daily',
    catchup=False,
    tags=['bigdata', 'huit', 'spark', 'hdfs', 'als_recommender'],
) as dag:

    start_pipeline = DummyOperator(
        task_id='start_pipeline'
    )

    # 1. Kiểm tra dữ liệu thô trên HDFS
    check_hdfs_data = BashOperator(
        task_id='check_hdfs_raw_data',
        bash_command='docker exec namenode hdfs dfs -test -e /data/raw/events.csv',
    )

    # 2. Thực thi Spark ETL phân tán (01_etl.py)
    run_spark_etl = BashOperator(
        task_id='run_spark_etl_pipeline',
        bash_command='docker exec spark-master /spark/bin/spark-submit --driver-memory 4g /spark/scripts/01_etl.py',
    )

    # 3. Chạy Spark SQL trích xuất Top Sản phẩm Cold-Start (01b_spark_sql_top_products.py)
    run_spark_sql_top_products = BashOperator(
        task_id='run_spark_sql_cold_start',
        bash_command='docker exec spark-master /spark/bin/spark-submit /spark/scripts/01b_spark_sql_top_products.py',
    )

    # 4. Huấn luyện mô hình học máy phân tán Spark MLlib ALS (02_train_als.py)
    train_als_model = BashOperator(
        task_id='train_distributed_als_model',
        bash_command='docker exec spark-master /spark/bin/spark-submit --driver-memory 4g /spark/scripts/02_train_als.py',
    )

    # 5. Chạy benchmark kiểm tra hiệu năng định lượng (03_benchmark.py)
    run_benchmark = BashOperator(
        task_id='run_performance_benchmark',
        bash_command='docker exec spark-master /spark/bin/spark-submit /spark/scripts/03_benchmark.py',
    )

    end_pipeline = DummyOperator(
        task_id='pipeline_completed_successfully'
    )

    # Thiết lập thứ tự thực thi trong đồ thị có hướng DAG
    start_pipeline >> check_hdfs_data >> run_spark_etl
    run_spark_etl >> run_spark_sql_top_products
    run_spark_etl >> train_als_model
    [run_spark_sql_top_products, train_als_model] >> run_benchmark >> end_pipeline
