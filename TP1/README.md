## TP1 : Cluster Benchmarking 

#### Install

1. AWS CLI [here](https://aws.amazon.com/cli/)
2. EB CLI [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)

Project is divided in three parts.

#### 1. App

Python web app, start using 
```shell
$ cd app/
$ pip install -r requirements.txt
$ gunicorn --bind 0.0.0.0:5000 app:app
```

#### 2. Benchmarking

```shell
$ cd benchmarking
$ docker-compose up --build
```


#### 3. Deploy

```shell
$ cd app/
$ eb init LOG8415E-TP1 --region us-east-1 --platform python-3.8
$  eb create cluster1-env 
```

to deploy a new version
```shell
$ eb deploy cluster1-env
```

If you would like to connect to an instance : 
```shell
eb ssh --setup
eb ssh cluster1-env
```