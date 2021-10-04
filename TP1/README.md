## TP1 : Cluster Benchmarking 

#### Install

1. AWS CLI [here](https://aws.amazon.com/cli/)
2. EB CLI [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)

Project is divided in three parts.

#### 1. App

Python web app, start using 
```shell
cd app/
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8000 app:app
```

#### 2. Benchmarking

```shell
cd benchmarking
docker-compose up --build
```


#### 3. Deploy

Create security group
```shell
# Create group
security_group=$(aws ec2 create-security-group \
                    --group-name=LOG8415E-TP1-ELB \
                    --description="Security group for LOG8415E-TP1. HTTP traffic allowed")

# Retrieve group id
group_id=$(echo $security_group | jq -rc .GroupId)

# Allow HTTP inbound trafic
aws ec2 authorize-security-group-ingress \
    --group-name=LOG8415E-TP1-ELB \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0
```

Create ELB
```shell
# Create ELB
lb=$(aws elbv2 create-load-balancer \
            --type application \
            --name LOG8415E-TP1-ELB  \
            --subnets subnet-0751162a8f498641c subnet-099ec60faafbd7e28 subnet-0fd3f4eab04f11b92 \
            --security-groups $group_id)

# Retrieve ELB ARN + URL
lb_arn=$(echo $lb | jq -r ".LoadBalancers[0].LoadBalancerArn" )
lb_url=$(echo $lb | jq -r ".LoadBalancers[0].DNSName" )

# Create HTTP listener
aws elbv2 create-listener \
    --load-balancer-arn $lb_arn \
    --protocol HTTP \
    --port 80  \
    --default-actions '{
            "Type": "fixed-response",
            "FixedResponseConfig": {
                "MessageBody": "LOG8415E-TP1-ELB",
                "StatusCode": "404",
                "ContentType": "text/plain"
            }
        }'
```

Init app
```shell
cd app/cluster<cluster_id>
eb init LOG8415E-TP1 --region us-east-1 --platform python-3.8
```

Create cluster1 environment
```shell
cluster_id=1

sed "s/{{CLUSTER_ID}}/$cluster_id/g" .ebextensions/shared_load-balancer.config.template \
    | sed "s/{{ELB_URL}}/$lb_url/" \
    > .ebextensions/shared_load-balancer.config

eb create cluster1-env \
    --instance_type "m4.large" \
    --envvars "CLUSTER_ID=$cluster_id" \
    --elb-type application \
    --shared-lb LOG8415E-TP1-ELB
```

Create cluster2 environment
```shell
cluster_id=2

sed "s/{{CLUSTER_ID}}/$cluster_id/g" .ebextensions/shared_load-balancer.config.template \
    | sed "s/{{ELB_URL}}/$lb_url/" \
    > .ebextensions/shared_load-balancer.config

eb create cluster2-env \
    --instance_type "t2.xlarge" \
    --envvars "CLUSTER_ID=$cluster_id" \
    --elb-type application \
    --shared-lb LOG8415E-TP1-ELB
```

To deploy a new app version
```shell
eb deploy cluster1-env
eb deploy cluster2-env
```

If you would like to connect to an instance
```shell
eb ssh --setup
eb ssh cluster1-env
```

#### 4. Teardown
```shell
# EB resources (Application, envs, app versions)
eb terminate --force --all
# Load balancer
aws elbv2 delete-load-balancer --load-balancer-arn $lb_arn
# Security group
aws ec2 delete-security-group --group-id $group_id
```