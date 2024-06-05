import boto3

def get_opensearch_endpoint(domain_name, region):
    client = boto3.client('es', region_name=region)
    response = client.describe_elasticsearch_domain(
        DomainName=domain_name
    )
    return response['DomainStatus']['Endpoint']