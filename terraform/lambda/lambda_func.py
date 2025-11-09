import json
import logging
import os

import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ecs_client = boto3.client("ecs")


def trigger_ecs_task_handler(event, context) -> dict:
    """Lambda function handler to trigger book data scraping
    & parsing as an ECS task.

    :param event: Lambda event data.
    :param context: Lambda context object.
    :return: Response containing task status information.
    """
    cluster_name = os.environ.get("CLUSTER_NAME")
    task_definition = os.environ.get("TASK_DEFINITION")
    subnet_id = os.environ.get("SUBNET_ID")
    security_group_id = os.environ.get("SECURITY_GROUP_ID")

    params = {
        "cluster": cluster_name,
        "taskDefinition": task_definition,
        "count": 1,
        "launchType": "FARGATE",
        "networkConfiguration": {
            "awsvpcConfiguration": {
                "subnets": [subnet_id],
                "securityGroups": [security_group_id],
                "assignPublicIp": "ENABLED",
            }
        },
    }

    try:
        response = ecs_client.run_task(**params)
        logger.info(f"ECS task started: {json.dumps(response, default=str)}")

        task_arn = (
            response.get("tasks")[0].get("taskArn")
            if response.get("tasks")
            else None
        )

        response = {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Book data scraping & parsing task "
                    "started successfully",
                    "taskArn": task_arn,
                }
            ),
        }

        return response
    except Exception as exc:
        raise exc
