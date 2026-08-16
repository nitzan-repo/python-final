import boto3

ec2 = boto3.client('ec2')
ssm = boto3.client('ssm', region_name='us-east-1')


def get_latest_ubuntu_ami():
    """ Automatically takes the latest version of Ubuntu AMI from SSM"""
    try:
        parameter = ssm.get_parameter(
            Name='/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id'
        )
        return parameter['Parameter']['Value']
    except Exception as e:
        print(f"Error fetching AMI: {e}")
        return None


def get_cli_instances():
    """ Shows CLI created instances """
    filters = [{'Name': 'tag:CreatedBy', 'Values': ['platform-cli']}]
    response = ec2.describe_instances(Filters=filters)
    instances = []
    for res in response['Reservations']:
        for inst in res['Instances']:
            if inst['State']['Name'] != 'terminated':
                instances.append(inst)
    return instances


def is_cli_instance(instance_id):
    """ Checks if instance is created by CLI """
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        tags = response['Reservations'][0]['Instances'][0].get('Tags', [])
        return any(t['Key'] == 'CreatedBy' and t['Value'] == 'platform-cli' for t in tags)
    except:
        return False


def create_instance(ami, instance_type):

    # (Instance type: only t3.micro or t2.small)
    allowed_types = ['t3.micro', 't2.small']
    if instance_type not in allowed_types:
        raise ValueError(f"Invalid instance type: {instance_type}. Allowed types are: {allowed_types}")

    # Hard cap (no more than 2 running instances)
    active_instances = [i for i in get_cli_instances() if i['State']['Name'] in ['running', 'pending']]
    if len(active_instances) >= 2:
        raise Exception("Hard cap reached: Cannot have more than 2 running/pending instances created by this CLI.")

    # the actual creating part with the needed tags
    return ec2.run_instances(
        ImageId=ami,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'CreatedBy', 'Value': 'platform-cli'},
                {'Key': 'Owner', 'Value': 'nitzan'},
                {'Key': 'Project', 'Value': 'python-final'}
            ]
        }]
    )


def start_instance(instance_id):
    ec2.start_instances(InstanceIds=[instance_id])


def stop_instance(instance_id):
    ec2.stop_instances(InstanceIds=[instance_id])


def update_instance_type(instance_id, new_instance_type):
    """updates instance type (t3.micro or t2.small)"""
    allowed_types = ['t3.micro', 't2.small']
    if new_instance_type not in allowed_types:
        raise ValueError(f"Invalid instance type: {new_instance_type}")

    if not is_cli_instance(instance_id):
        raise PermissionError("Access Denied: This instance was not created by the CLI.")

    #stops the instance before updating
    state = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]['State']['Name']

    if state == 'running':
        stop_instance(instance_id)
        # wait until the instance actually stops before a wrong output
        waiter = ec2.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[instance_id])

    ec2.modify_instance_attribute(
        InstanceId=instance_id,
        InstanceType={'Value': new_instance_type}
    )


def terminate_instance(instance_id):
    if not is_cli_instance(instance_id):
        raise PermissionError("Access Denied: This instance was not created by the CLI.")
    return ec2.terminate_instances(InstanceIds=[instance_id])
