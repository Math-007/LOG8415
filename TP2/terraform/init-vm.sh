#!/bin/bash -e

# Constants
VM_USER="azureuser"
HADOOP_VERSION="3.3.1"
SPARK_VERSION="3.2.0"

HADOOP_DOWNLOAD_URL="https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz"
HADOOP_SIGNATURE_URL="https://downloads.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz.asc"
HADOOP_KEYS_URL="https://downloads.apache.org/hadoop/common/KEYS"

SPARK_DOWNLOAD_URL="https://dlcdn.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.2.tgz"
SPARK_SIGNATURE_URL="https://downloads.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.2.tgz.asc"
SPARK_KEYS_URL="https://downloads.apache.org/spark/KEYS"

HADOOP_HOME="/opt/hadoop"
SPARK_HOME="/opt/spark"

# Hadoop
## Get binary
wget -O /tmp/hadoop.tar.gz $HADOOP_DOWNLOAD_URL
## Get signature & keys
wget -O /tmp/hadoop.tar.gz.asc $HADOOP_SIGNATURE_URL
wget -O /tmp/hadoop_keys $HADOOP_KEYS_URL
## Verify signature
gpg --import /tmp/hadoop_keys
gpg --verify /tmp/hadoop.tar.gz.asc /tmp/hadoop.tar.gz
## Unarchive in HADOOP_HOME
tar xf /tmp/hadoop.tar.gz -C /tmp/
sudo mv "/tmp/hadoop-$HADOOP_VERSION/" $HADOOP_HOME

# Get Spark
## Get binary
wget -O /tmp/spark.tar.gz $SPARK_DOWNLOAD_URL
## Get signature & keys
wget -O /tmp/spark.tar.gz.asc $SPARK_SIGNATURE_URL
wget -O /tmp/spark_keys $SPARK_KEYS_URL
## Verify signature
gpg --import /tmp/spark_keys
gpg --verify /tmp/spark.tar.gz.asc /tmp/spark.tar.gz
## Unarchive in SPARK_HOME
tar xf /tmp/spark.tar.gz -C /tmp/
sudo mv "/tmp/spark-$SPARK_VERSION-bin-hadoop3.2/" $SPARK_HOME

# Install required packages
sudo apt-get update \
    && sudo apt-get install -y python3 default-jdk-headless

# Update bashrc
cat <<EOF >> /home/$VM_USER/.bashrc

# Spark
export SPARK_HOME=$SPARK_HOME
export PATH=\$PATH:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
export PYSPARK_PYTHON=/usr/bin/python3

# Hadoop
export HADOOP_HOME=$HADOOP_HOME
export HADOOP_INSTALL=\$HADOOP_HOME
export HADOOP_MAPRED_HOME=\$HADOOP_HOME
export HADOOP_COMMON_HOME=\$HADOOP_HOME
export HADOOP_HDFS_HOME=\$HADOOP_HOME
export YARN_HOME=\$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=\$HADOOP_HOME/lib/native
export PATH=\$PATH:\$HADOOP_HOME/sbin:\$HADOOP_HOME/bin
export HADOOP_OPTS="-Djava.library.path=\$HADOOP_HOME/lib/native"
export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$HADOOP_HOME/lib/native
export JAVA_HOME=/usr/lib/jvm/default-java
EOF

# Download dataset
# TODO