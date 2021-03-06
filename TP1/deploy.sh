#!/bin/bash

# ╔═══════════╗
# ║ Constants ║
# ╚═══════════╝

# Color
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color

# Names
ELB_NAME='LOG8415E-TP1-ELB'

# Instances
# CLUSTER_1_INSTANCE_TYPE="m4.large"
# CLUSTER_2_INSTANCE_TYPE="t2.xlarge"
CLUSTER_1_INSTANCE_TYPE="t2.micro"
CLUSTER_2_INSTANCE_TYPE="t2.micro"

# Other
START=`date +%s`

# Disable `less` output of awscli
export AWS_PAGER="" 

# ╔═══════════╗
# ║ Functions ║
# ╚═══════════╝

function print_progress() {
    echo -e "${BLUE}===============:${NC} $1 ${BLUE}:===============${NC}"
}

function print_warning() {
    echo -e "${YELLOW}Warning: $1$NC"
}

function print_success() {
    echo -e "${GREEN}===============:${NC} $1 ${GREEN}:===============${NC}"
}

function print_error() {
    echo -e "${RED}Error: $1$NC"
}

# ╔════════╗
# ║ Checks ║
# ╚════════╝

# Check if jq is installed
# https://stackoverflow.com/a/677212
if ! command -v jq &> /dev/null
then
    print_error "jq not found. Please install it."
    exit -1
fi

# Check if ebcli is installed
if ! command -v aws &> /dev/null
then
    print_error "awscli not found. Please install it: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
    exit -1
fi

# Check if ebcli is installed
if ! command -v eb &> /dev/null
then
    print_error "ebcli not found. Please install it: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html"
    exit -1
fi

# Check current folder 
if [[ ! -f "app.py" && ! -d ".ebextensions" ]];
then
    print_error "deploy.sh must be run alongside app.py and .ebextensions."
    exit -1
fi

# Check if awscli is configured
aws ec2 create-security-group \
    --dry-run \
    --group-name="test-$(date +%s)" \
    --description="Test security group." 2> /dev/null
dummy_create_status=$?

if [[ ! $dummy_create_status -eq 254 ]];
then
    print_error "Can't create dummy security group. Please check aws cli configuration."
    exit -1
fi

# Exit when any command fails
set -e

# ╔════════════════╗
# ║ Security Group ║
# ╚════════════════╝

print_progress "Creating security group"

# Create group
security_group=$(aws ec2 create-security-group \
                    --group-name=$ELB_NAME \
                    --description="Security group for LOG8415E-TP1. HTTP traffic allowed")

# Retrieve group id
group_id=$(echo $security_group | jq -rc .GroupId)

# Allow HTTP inbound trafic
aws ec2 authorize-security-group-ingress \
    --group-name=$ELB_NAME \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

# ╔═══════════════╗
# ║ Load-Balancer ║
# ╚═══════════════╝


subnet_id_a=$(aws ec2 describe-subnets \
  --filters Name=availabilityZone,Values=us-east-1a | jq -r '.Subnets[0].SubnetId'
  )

subnet_id_b=$(aws ec2 describe-subnets \
  --filters Name=availabilityZone,Values=us-east-1b | jq -r '.Subnets[0].SubnetId'
  )

print_progress "Creating load balancer"


# Create ELB
# Subnets are us-east-1a, us-east-1b
lb=$(aws elbv2 create-load-balancer \
            --type application \
            --name $ELB_NAME \
            --subnets $subnet_id_a $subnet_id_b \
            --security-groups $group_id)

# Retrieve ELB ARN & URL
lb_arn=$(echo $lb | jq -r ".LoadBalancers[0].LoadBalancerArn" )
lb_url=$(echo $lb | jq -r ".LoadBalancers[0].DNSName" )

# Create HTTP listener
# Default action is for debug purposes
aws elbv2 create-listener \
    --load-balancer-arn $lb_arn \
    --protocol HTTP \
    --port 80  \
    --default-actions '{
            "Type": "fixed-response",
            "FixedResponseConfig": {
                "MessageBody": "LOG8415E-TP1-ELB: Cannot route request",
                "StatusCode": "404",
                "ContentType": "text/plain"
            }
        }'

print_progress "Waiting for load balancer to be marked as active (may take a minute or two)"
aws elbv2 wait load-balancer-available --load-balancer-arns $lb_arn


# ╔═══════════════════╗
# ║ Elastic Beanstalk ║
# ╚═══════════════════╝

print_progress "Creating Elastic Beanstalk environments"

# Cleanup
rm -f .ebextensions/shared_load-balancer.config

# Init app
eb init LOG8415E-TP1 --region us-east-1 --platform python-3.8

#
# cluster 1
#
cluster_id=1

print_progress "Creating cluster 1"
print_warning "This may take a while"

# Generate shared load-balancer config from template
sed "s/{{CLUSTER_ID}}/$cluster_id/g" .ebextensions/shared_load-balancer.config.template \
    | sed "s/{{ELB_URL}}/$lb_url/" \
    > .ebextensions/shared_load-balancer.config

# Create cluster 1
eb create cluster1-env \
    --instance_type $CLUSTER_1_INSTANCE_TYPE \
    --envvars "CLUSTER_ID=$cluster_id" \
    --elb-type application \
    --shared-lb $ELB_NAME

#
# cluster 2
#
cluster_id=2

print_progress "Creating cluster 2"
print_warning "This may take a while"

# Generate shared load-balancer config from template
sed "s/{{CLUSTER_ID}}/$cluster_id/g" .ebextensions/shared_load-balancer.config.template \
    | sed "s/{{ELB_URL}}/$lb_url/" \
    > .ebextensions/shared_load-balancer.config

# Create cluster 2
eb create cluster2-env \
    --instance_type $CLUSTER_2_INSTANCE_TYPE \
    --envvars "CLUSTER_ID=$cluster_id" \
    --elb-type application \
    --shared-lb $ELB_NAME

# Cleanup
rm .ebextensions/shared_load-balancer.config


# ╔═════════╗
# ║ Success ║
# ╚═════════╝

# https://stackoverflow.com/a/20249473
END=`date +%s`
runtime=$( echo $((END-START)) | awk '{print int($1/60)" minutes "int($1%60)" seconds"}' )

print_success "Deployed in $runtime"
echo "Cluster1: $lb_url/cluster1"
echo "Cluster2: $lb_url/cluster2"
echo "Try it: watch -n 0.25 curl -s $lb_url/cluster1"