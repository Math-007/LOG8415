import logging
from datetime import datetime
from time import sleep

import boto3

from analytics import analytics
from benchmark import benchmark, benchmark_demo

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger("Benchmark App")


elb = boto3.client(service_name='elbv2', region_name='us-east-1')


def _get_data():
    load_balancers = elb.describe_load_balancers()
    load_balancer = [
        load_balancer for load_balancer in load_balancers['LoadBalancers']
        if load_balancer['LoadBalancerName'] == 'LOG8415E-TP1-ELB'
    ][0]

    load_balancer_host = load_balancer['DNSName']

    load_balancer_arn = load_balancer['LoadBalancerArn']
    describe_target_groups = elb.describe_target_groups(LoadBalancerArn=load_balancer_arn)

    target_groups_arn = [
        target_group['TargetGroupArn'].split(':')[-1]
        for target_group in describe_target_groups['TargetGroups']
    ]

    return load_balancer_host, target_groups_arn


def _benchmark_and_analytics_per_cluster(endpoint, target_group, cluster_id):
    logger.info(f"Starting benchmark cluster {cluster_id}")
    start_date = datetime.utcnow()
    # benchmark(endpoint)
    benchmark_demo(endpoint, cluster_id)
    end_date = datetime.utcnow()
    logger.info(f"Ending benchmark cluster {cluster_id}")

    logger.info(f"Starting analytics for cluster {cluster_id}")
    sleep(360)
    analytics(start_date, end_date, cluster_id, target_group)
    logger.info(f"Ending analytics for cluster {cluster_id}")


def main():
    logger.info("Starting application")

    logger.info("Getting load balancer")
    load_balancer_host, target_groups = _get_data()

    endpoint_1 = f'http://{load_balancer_host}/cluster1'
    endpoint_2 = f'http://{load_balancer_host}/cluster2'

    _benchmark_and_analytics_per_cluster(endpoint_1, target_groups[0], 1)
    _benchmark_and_analytics_per_cluster(endpoint_2, target_groups[1], 2)


if __name__ == '__main__':
    main()
