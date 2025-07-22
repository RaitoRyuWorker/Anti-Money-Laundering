#!/bin/bash

echo "Copying Hadoop AWS jar..."
docker cp spark-master:/opt/bitnami/spark/jars/hadoop-aws-3.3.4.jar ./shared/jars/hadoop-aws-3.3.4.jar

echo "Copying AWS SDK bundle jar..."
docker cp spark-master:/opt/bitnami/spark/jars/aws-java-sdk-bundle-1.12.262.jar ./shared/jars/aws-java-sdk-bundle-1.12.262.jar

echo "Done copying jars into ./shared/jars/"
