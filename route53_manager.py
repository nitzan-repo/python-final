import boto3

route53_client = boto3.client('route53')
TAG_KEY_CREATED = "CreatedBy"
TAG_VAL_CREATED = "platform-cli"
TAG_KEY_OWNER = "Owner"
TAG_VAL_OWNER = "nitzan"


def create_hosted_zone(domain_name, vpc_id=None, vpc_region='us-east-1'):
    # create new hosted zone public or private (if a vpc is mentioned)
    params = {
        'Name': domain_name,
        'CallerReference': str(hash(domain_name + str(vpc_id))),
        'HostedZoneConfig': {
            'Comment': 'Created by Platform CLI',
            'PrivateZone': bool(vpc_id)
        }
    }

    if vpc_id:
        params['VPC'] = {
            'VPCRegion': vpc_region,
            'VPCId': vpc_id
        }

    response = route53_client.create_hosted_zone(**params)
    zone_id = response['HostedZone']['Id']

    #tags
    route53_client.change_tags_for_resource(
        ResourceType='hostedzone',
        ResourceId=zone_id.split('/')[-1],
        AddTags=[
            {'Key': TAG_KEY_CREATED, 'Value': TAG_VAL_CREATED},
            {'Key': TAG_KEY_OWNER, 'Value': TAG_VAL_OWNER}
        ]
    )
    return zone_id


def list_cli_hosted_zones():
    """ show all CLI hosted zones, distinguish by tags"""
    zones = route53_client.list_hosted_zones()['HostedZones']
    cli_zones = []

    for zone in zones:
        zone_id = zone['Id'].split('/')[-1]
        tags = route53_client.list_tags_for_resource(ResourceType='hostedzone', ResourceId=zone_id)
        tag_list = tags['ResourceTagSet']['Tags']

        # new list for cli zones
        if any(tag['Key'] == TAG_KEY_CREATED and tag['Value'] == TAG_VAL_CREATED for tag in tag_list):
            cli_zones.append(zone)

    return cli_zones


def delete_hosted_zone(zone_id):
    # delete hosed zone
    tags = route53_client.list_tags_for_resource(ResourceType='hostedzone', ResourceId=zone_id)
    tag_list = tags['ResourceTagSet']['Tags']

    if not any(tag['Key'] == TAG_KEY_CREATED and tag['Value'] == TAG_VAL_CREATED for tag in tag_list):
        raise Exception("Permission Denied: Cannot delete a zone that was not created by this CLI.")

    return route53_client.delete_hosted_zone(Id=zone_id)


def upsert_record(zone_id, record_name, record_type, record_value, ttl=300):
    # create or update DNS record in the hosted zone
    response = route53_client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Comment': 'Managed by Platform CLI',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': record_name,
                        'Type': record_type,
                        'TTL': ttl,
                        'ResourceRecords': [{'Value': record_value}]
                    }
                }
            ]
        }
    )
    return response


def delete_record(zone_id, record_name, record_type, record_value):
    # delete a DNS record in the hosted zone
    response = route53_client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Comment': 'Deleted by Platform CLI',
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': record_name,
                        'Type': record_type,
                        'TTL': 300,
                        'ResourceRecords': [{'Value': record_value}]
                    }
                }
            ]
        }
    )
    return response
