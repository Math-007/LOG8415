# TP2

## Word count

### Hadoop

Compile:
```shell
cd wordcount/hadoop
hadoop com.sun.tools.javac.Main WordCount.java
jar cf word-count-hadoop.jar WordCount*.class
rm -f *.class
```
Execute:
```shell
hdfs dfs -rm -r output
hadoop jar word-count-hadoop.jar WordCount ../../dataset output
```

### Spark

Compile:
```shell
cd wordcount/spark
mvn package
```
Execute:
```shell
hdfs dfs -rm -r output
spark-submit --class WordCount target/word-count-spark-1.0-jar-with-dependencies.jar ../../dataset output
```

## Terraform

### Create VM:
```shell
cd terraform
az login
terraform init
terraform apply
```

### SSH in VM
```shell
terraform output -raw tls_private_key > key.pem
chmod 400 key.pem
ip=$(terraform output -raw public_ip_address)
ssh azureuser@$ip -i key.pem
```
