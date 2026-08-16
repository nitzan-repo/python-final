import click
import ec2_manager
import s3_manager
import route53_manager

# --- cli.py Commands Group ---
@click.group()
def cli():
    """Cloud and AWS Management CLI System"""
    pass

# --- EC2 Commands Group ---
@cli.group()
def ec2_ops():
    """Manage EC2 resources"""
    pass

@ec2_ops.command()
@click.option('--instance-type', type=click.Choice(['t3.micro', 't2.small']), default='t3.micro', help="Instance type")
@click.option('--ami', required=False, help="Optional AMI ID (will fetch latest Ubuntu automatically if omitted)")
def create(instance_type, ami):
    """Create a new EC2 instance"""
    active_instances = [i for i in ec2_manager.get_cli_instances() if i['State']['Name'] in ['running', 'pending']]
    if len(active_instances) >= 2:
        click.echo("Error: Hard cap reached! Cannot create more than 2 running instances created by this CLI.")
        return

    if not ami:
        click.echo("No AMI provided. Fetching latest Ubuntu AMI from SSM...")
        ami = ec2_manager.get_latest_ubuntu_ami()
        if not ami:
            click.echo("Error: Failed to fetch latest AMI automatically.")
            return
        click.echo(f"Using AMI: {ami}")

    try:
        res = ec2_manager.create_instance(ami, instance_type)
        instance_id = res['Instances'][0]['InstanceId']
        click.echo(f"Success! Created instance ID: {instance_id}")
    except Exception as e:
        click.echo(f"Failed to create instance: {e}")

@ec2_ops.command()
def list():
    """List all CLI-created instances"""
    instances = ec2_manager.get_cli_instances()
    if not instances:
        click.echo("No CLI-created instances found.")
        return
    for inst in instances:
        click.echo(f"ID: {inst['InstanceId']} | State: {inst['State']['Name']} | Type: {inst['InstanceType']}")

@ec2_ops.command()
@click.option('--instance-id', required=True, help="Instance ID to start")
def start(instance_id):
    """Start a CLI-created instance"""
    if ec2_manager.is_cli_instance(instance_id):
        ec2_manager.start_instance(instance_id)
        click.echo(f"Successfully started instance: {instance_id}")
    else:
        click.echo("Error: Access denied. This instance was not created by the CLI.")

@ec2_ops.command()
@click.option('--instance-id', required=True, help="Instance ID to stop")
def stop(instance_id):
    """Stop a CLI-created instance"""
    if ec2_manager.is_cli_instance(instance_id):
        ec2_manager.stop_instance(instance_id)
        click.echo(f"Successfully stopped instance: {instance_id}")
    else:
        click.echo("Error: Access denied. This instance was not created by the CLI.")

@ec2_ops.command()
@click.option('--instance-id', required=True, help="Instance ID to update")
@click.option('--instance-type', type=click.Choice(['t3.micro', 't2.small']), required=True, help="New instance type")
def update(instance_id, instance_type):
    """Update EC2 instance type (will stop instance automatically if running)"""
    try:
        ec2_manager.update_instance_type(instance_id, instance_type)
        click.echo(f"Successfully updated instance {instance_id} to type {instance_type}")
    except Exception as e:
        click.echo(f"Failed to update instance: {e}")

@ec2_ops.command()
@click.option('--instance-id', required=True, help="Instance ID to terminate")
def delete(instance_id):
    """Terminate (delete) a CLI-created instance"""
    try:
        ec2_manager.terminate_instance(instance_id)
        click.echo(f"Successfully terminated instance: {instance_id}")
    except Exception as e:
        click.echo(f"Failed to terminate instance: {e}")


# --- S3 Commands Group ---
@cli.group()
def s3_ops():
    """Manage S3 resources"""
    pass

@s3_ops.command()
@click.option('--name', required=True, help="Name of the S3 bucket (must be globally unique)")
@click.option('--visibility', type=click.Choice(['private', 'public']), default='private', help="Bucket visibility")
def create(name, visibility):
    """Create a new S3 bucket (private or public)"""
    is_public = (visibility == 'public')

    # s3 type - if public, a special approval is needed
    if is_public:
        click.echo("WARNING: You are about to create a PUBLIC S3 bucket[cite: 1].")
        confirmation = click.prompt("Are you sure? (yes/no)", type=str)
        if confirmation.lower() != 'yes':
            click.echo("Operation cancelled.")
            return

    try:
        s3_manager.create_bucket(name, is_public=is_public)
        click.echo(f"Success! Created S3 bucket: {name} (Visibility: {visibility})")
    except Exception as e:
        click.echo(f"Failed to create bucket: {e}")

@s3_ops.command()
@click.option('--bucket', required=True, help="Bucket name")
@click.option('--file', required=True, help="Path to local file to upload")
def upload(bucket, file):
    """Upload a file """
    try:
        s3_manager.upload_file_to_bucket(bucket, file)
        click.echo(f"Successfully uploaded {file} to bucket {bucket}")
    except Exception as e:
        click.echo(f"Upload failed: {e}")

@s3_ops.command()
@click.option('--bucket', required=True, help="Name of the S3 bucket")
@click.option('--file', required=True, help="Name/key of the file to delete")
def delete_file(bucket, file):
    """Delete a file from an S3 bucket"""
    try:
        s3_manager.delete_file_from_bucket(bucket, file)
        click.echo(f"Successfully deleted file '{file}' from bucket '{bucket}'")
    except Exception as e:
        click.echo(f"Failed to delete file: {e}")


@s3_ops.command()
@click.option('--bucket', required=True, help="Name of the S3 bucket to list files from")
def list_files(bucket):
    """List all files in a specific CLI-created S3 bucket"""
    try:
        files = s3_manager.list_bucket_files(bucket)
        if not files:
            click.echo(f"The bucket '{bucket}' is empty.")
        else:
            click.echo(f"Files in bucket '{bucket}':")
            for file in files:
                click.echo(f"- {file}")
    except PermissionError as e:
        click.echo(f"Access Denied: {e}")
    except Exception as e:
        click.echo(f"Failed to list files: {e}")


@s3_ops.command()
def list():
    """Show only CLI-created buckets"""
    buckets = s3_manager.get_cli_buckets()
    if not buckets:
        click.echo("No CLI-created S3 buckets found.")
        return
    click.echo("CLI-created S3 Buckets:")
    for b in buckets:
        click.echo(f" - {b}")

@s3_ops.command()
@click.option('--name', required=True, help="Bucket name to update")
@click.option('--visibility', type=click.Choice(['private', 'public']), required=True, help="New visibility")
def update(name, visibility):
    """Update S3 bucket visibility (private/public)"""
    is_public = (visibility == 'public')

    if is_public:
        click.echo("WARNING: You are about to make this S3 bucket PUBLIC.")
        confirmation = click.prompt("Are you sure? (yes/no)", type=str)
        if confirmation.lower() != 'yes':
            click.echo("Operation cancelled.")
            return

    try:
        s3_manager.update_bucket_visibility(name, is_public)
        click.echo(f"Successfully updated bucket {name} visibility to {visibility}")
    except Exception as e:
        click.echo(f"Failed to update bucket: {e}")

@s3_ops.command()
@click.option('--name', required=True, help="Bucket name to delete (must be empty)")
def delete(name):
    """Delete a CLI-created S3 bucket"""
    try:
        s3_manager.delete_bucket(name)
        click.echo(f"Successfully deleted S3 bucket: {name}")
    except Exception as e:
        click.echo(f"Failed to delete bucket (make sure it is empty): {e}")

# --- route53 Commands Group ---
@cli.group()
def route53_ops():
    """Manage Route53 DNS resources"""
    pass

@route53_ops.command()
@click.option('--name', required=True, help="Domain name for the Hosted Zone")
@click.option('--vpc-id', required=False, help="Optional VPC ID for a Private Hosted Zone")
def create_zone(name, vpc_id):
    """Create a new Hosted Zone (Public or Private)"""
    try:
        zone_id = route53_manager.create_hosted_zone(name, vpc_id=vpc_id)
        zone_type = "Private" if vpc_id else "Public"
        click.echo(f"Success! Created {zone_type} Hosted Zone {name} with ID: {zone_id}")
    except Exception as e:
        click.echo(f"Failed to create hosted zone: {e}")


@route53_ops.command()
def list_zones():
    """Show only CLI-created Hosted Zones"""
    zones = route53_manager.list_cli_hosted_zones()
    if not zones:
        click.echo("No CLI-created Hosted Zones found.")
        return
    click.echo("CLI-created Hosted Zones:")
    for z in zones:
        click.echo(f" - ID: {z['Id'].split('/')[-1]} | Name: {z['Name']}")

@route53_ops.command()
@click.option('--zone-id', required=True, help="Hosted Zone ID to delete")
def delete_zone(zone_id):
    """Delete a CLI-created Hosted Zone"""
    try:
        route53_manager.delete_hosted_zone(zone_id)
        click.echo(f"Successfully deleted Hosted Zone: {zone_id}")
    except Exception as e:
        click.echo(f"Failed to delete hosted zone: {e}")

@route53_ops.command()
@click.option('--zone-id', required=True, help="Hosted Zone ID")
@click.option('--name', required=True, help="Record name (e.g., www.nitzan.local.)")
@click.option('--type', required=True, default='A', help="Record type (A, CNAME, etc.)")
@click.option('--value', required=True, help="Record value (e.g., IP address)")
def upsert_record(zone_id, name, type, value):
    """Create or update a DNS record in a CLI-created zone"""
    try:
        route53_manager.upsert_record(zone_id, name, type, value)
        click.echo(f"Successfully upserted record {name} ({type}) in zone {zone_id}")
    except Exception as e:
        click.echo(f"Failed to upsert record: {e}")

@route53_ops.command()
@click.option('--zone-id', required=True, help="Hosted Zone ID")
@click.option('--name', required=True, help="Record name")
@click.option('--type', required=True, default='A', help="Record type")
@click.option('--value', required=True, help="Record value")
def delete_record(zone_id, name, type, value):
    """Delete a DNS record from a CLI-created zone"""
    try:
        route53_manager.delete_record(zone_id, name, type, value)
        click.echo(f"Successfully deleted record {name} ({type}) from zone {zone_id}")
    except Exception as e:
        click.echo(f"Failed to delete record: {e}")

# Adding the groups to thr primary group commands
cli.add_command(ec2_ops)
cli.add_command(s3_ops)
cli.add_command(route53_ops)

if __name__ == '__main__':
    cli()
