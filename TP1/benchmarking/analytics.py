from datetime import timedelta
from pathlib import Path

import boto3
import matplotlib.pyplot as plt

cloudwatch = boto3.client(service_name='cloudwatch', region_name='us-east-1')


def _extract_metric(start_time, end_time, cluster_id, metric_name, statistic, dimensions):
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/ApplicationELB',
        Period=1,
        StartTime=start_time - timedelta(minutes=3),
        EndTime=end_time + timedelta(minutes=5),
        MetricName=metric_name,
        Statistics=[statistic],
        Dimensions=dimensions
    )

    response['Datapoints'].sort(key=lambda d: d['Timestamp'])
    x = [d['Timestamp'] for d in response['Datapoints']]
    y = [d[statistic] for d in response['Datapoints']]

    fig1, ax1 = plt.subplots()

    ax1.title.set_text(f'cluster {cluster_id}: {metric_name} - {statistic}')
    ax1.set_xlabel(statistic)
    ax1.set_xlabel('Time')
    ax1.grid()
    ax1.plot(x, y, '-o')

    fig1.savefig(f'img/cluster_{cluster_id}_{metric_name}_{statistic}')
    plt.close(fig1)


def analytics(start_time, end_time, cluster_id, target_group):
    Path("img/").mkdir(parents=True, exist_ok=True)

    dimensions = [
        {
            'Name': 'LoadBalancer',
            'Value': 'app/LOG8415E-TP1-ELB/34b9577b1309f9c3'
        },
        {
            "Name": "TargetGroup",
            "Value": target_group
        }
    ]

    load_balancer_dimensions = [
        {
            'Name': 'LoadBalancer',
            'Value': 'app/LOG8415E-TP1-ELB/34b9577b1309f9c3'
        },
    ]

    _extract_metric(start_time, end_time, cluster_id, "RequestCount", "Sum", dimensions)
    _extract_metric(start_time, end_time, cluster_id, "RequestCount", "Average", dimensions)

    _extract_metric(start_time, end_time, cluster_id, "RequestCountPerTarget", "Sum", dimensions)
    _extract_metric(start_time, end_time, cluster_id, "RequestCountPerTarget", "Average", dimensions)

    _extract_metric(start_time, end_time, cluster_id, "TargetResponseTime", "Average", dimensions)

    _extract_metric(start_time, end_time, cluster_id, "ProcessedBytes", "Sum", load_balancer_dimensions)
    _extract_metric(start_time, end_time, cluster_id, "ProcessedBytes", "Average", load_balancer_dimensions)

