import logging
from datetime import datetime
from time import sleep

import boto3

from analytics import analytics
from benchmark import benchmark

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger("Benchmark App")


elb = boto3.client(service_name='elbv2', region_name='us-east-1')


def _benchmark_and_analytics_per_cluster(endpoint, target_group, cluster_id):
    logger.info(f"Starting benchmark cluster {cluster_id}")
    start_date = datetime.utcnow()
    benchmark(endpoint)
    end_date = datetime.utcnow()
    logger.info(f"Ending benchmark cluster {cluster_id}")

    logger.info(f"Starting analytics for cluster {cluster_id}")
    sleep(360)
    analytics(start_date, end_date, cluster_id, target_group)
    logger.info(f"Ending analytics for cluster {cluster_id}")


def main():
    logger.info("Starting application")

    logger.info("Getting load balancer")

    load_balancers = elb.describe_load_balancers()
    load_balancer = [
        load_balancer for load_balancer in load_balancers['LoadBalancers']
        if load_balancer['LoadBalancerName'] == 'LOG8415E-TP1-ELB'
    ][0]

    load_balancer_arn = load_balancer['LoadBalancerArn']
    load_balancer_host = load_balancer['DNSName']

    endpoint_1 = f'http://{load_balancer_host}/cluster1'
    endpoint_2 = f'http://{load_balancer_host}/cluster2'

    _benchmark_and_analytics_per_cluster(endpoint_1, "targetgroup/awseb-cluster1-default-2wscr/1905e74e7bea1463", 1)
    _benchmark_and_analytics_per_cluster(endpoint_2, "targetgroup/awseb-cluster2-default-gj59n/8a581d8a8527c3b9", 2)


if __name__ == '__main__':
    main()
