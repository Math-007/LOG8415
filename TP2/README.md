# TP2

## Word count

### Hadoop

Compile:
```shell
cd wordcount/hadoop
hadoop com.sun.tools.javac.Main WordCount.java
jar cf wc.jar WordCount*.class
```
Execute:
```shell
hdfs dfs -rm -r output
hadoop jar wc.jar WordCount ../../dataset output
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
