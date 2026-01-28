#!/usr/bin/env python3
"""
AWS EC2 Instance Information Fetcher with Open Ports
Fetches all EC2 instance names, IP addresses, and open ports from security groups
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def get_security_group_rules(ec2_client, security_group_ids):
    """
    Get inbound rules from security groups and return open ports
    """
    open_ports = []
    
    try:
        if not security_group_ids:
            return "No SG"
        
        # Get security group details
        response = ec2_client.describe_security_groups(GroupIds=security_group_ids)
        
        for sg in response['SecurityGroups']:
            sg_name = sg['GroupName']
            
            for rule in sg.get('IpPermissions', []):
                # Get port range
                from_port = rule.get('FromPort', 'All')
                to_port = rule.get('ToPort', 'All')
                protocol = rule.get('IpProtocol', 'All')
                
                # Convert protocol number to name
                if protocol == '-1':
                    protocol = 'All'
                elif protocol == '6':
                    protocol = 'TCP'
                elif protocol == '17':
                    protocol = 'UDP'
                elif protocol == '1':
                    protocol = 'ICMP'
                
                # Check source (is it open to internet?)
                sources = []
                
                # Check IPv4 ranges
                for ip_range in rule.get('IpRanges', []):
                    cidr = ip_range.get('CidrIp', '')
                    if cidr == '0.0.0.0/0':
                        sources.append('0.0.0.0/0 (PUBLIC)')
                    else:
                        sources.append(cidr)
                
                # Check IPv6 ranges
                for ip_range in rule.get('Ipv6Ranges', []):
                    cidr = ip_range.get('CidrIpv6', '')
                    if cidr == '::/0':
                        sources.append('::/0 (PUBLIC)')
                    else:
                        sources.append(cidr)
                
                # Check security group sources
                for sg_ref in rule.get('UserIdGroupPairs', []):
                    sources.append(f"SG:{sg_ref.get('GroupId', 'Unknown')}")
                
                if not sources:
                    sources = ['Unknown']
                
                # Format port info
                if from_port == to_port:
                    port_info = f"{from_port}/{protocol}"
                elif from_port == 'All':
                    port_info = f"All/{protocol}"
                else:
                    port_info = f"{from_port}-{to_port}/{protocol}"
                
                # Add source info
                source_str = ', '.join(sources[:2])  # Limit to first 2 sources for readability
                if len(sources) > 2:
                    source_str += f" +{len(sources)-2} more"
                
                open_ports.append(f"{port_info} from {source_str}")
        
        return '; '.join(open_ports) if open_ports else "No inbound rules"
    
    except Exception as e:
        return f"Error: {str(e)[:30]}"

def get_ec2_instances_with_ports():
    """
    Fetch all EC2 instances with their names, IP addresses, and open ports
    """
    try:
        # Create EC2 client using default AWS config
        ec2_client = boto3.client('ec2')
        
        # Describe all EC2 instances
        response = ec2_client.describe_instances()
        
        instances = []
        
        print(f"Found instances. Analyzing security groups...\n")
        
        # Parse through all reservations and instances
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Extract instance name from tags
                instance_name = 'N/A'
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break
                
                # Extract basic info
                instance_id = instance['InstanceId']
                state = instance['State']['Name']
                private_ip = instance.get('PrivateIpAddress', 'N/A')
                public_ip = instance.get('PublicIpAddress', 'N/A')
                instance_type = instance.get('InstanceType', 'N/A')
                
                # Get security groups
                security_groups = instance.get('SecurityGroups', [])
                sg_ids = [sg['GroupId'] for sg in security_groups]
                sg_names = [sg['GroupName'] for sg in security_groups]
                
                # Get open ports from security groups
                print(f"Processing: {instance_name} ({instance_id})")
                open_ports = get_security_group_rules(ec2_client, sg_ids)
                
                instances.append({
                    'Name': instance_name,
                    'Instance ID': instance_id,
                    'State': state,
                    'Private IP': private_ip,
                    'Public IP': public_ip,
                    'Instance Type': instance_type,
                    'Security Groups': ', '.join(sg_names) if sg_names else 'None',
                    'Open Ports/Rules': open_ports
                })
        
        return instances
    
    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your AWS credentials.")
        print("Run 'aws configure' or set up your credentials file.")
        return None
    
    except ClientError as e:
        print(f"Error accessing AWS: {e}")
        return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def print_instances(instances):
    """
    Print instances in a formatted way
    """
    if not instances:
        print("No EC2 instances found.")
        return
    
    print(f"\n{'='*150}")
    print(f"Found {len(instances)} EC2 instance(s)")
    print(f"{'='*150}\n")
    
    for instance in instances:
        print(f"Name:            {instance['Name']}")
        print(f"Instance ID:     {instance['Instance ID']}")
        print(f"State:           {instance['State']}")
        print(f"Instance Type:   {instance['Instance Type']}")
        print(f"Private IP:      {instance['Private IP']}")
        print(f"Public IP:       {instance['Public IP']}")
        print(f"Security Groups: {instance['Security Groups']}")
        print(f"Open Ports:      {instance['Open Ports/Rules']}")
        
        # Highlight if publicly accessible
        if 'PUBLIC' in instance['Open Ports/Rules'] and instance['Public IP'] != 'N/A':
            print("⚠️  WARNING: Instance has public IP and publicly accessible ports!")
        
        print("-" * 150)

def print_summary(instances):
    """
    Print a summary of security findings
    """
    public_instances = []
    
    for instance in instances:
        if 'PUBLIC' in instance['Open Ports/Rules'] and instance['Public IP'] != 'N/A':
            public_instances.append(instance)
    
    if public_instances:
        print(f"\n⚠️  SECURITY SUMMARY: {len(public_instances)} instance(s) with public IP and publicly accessible ports:")
        print("-" * 150)
        for inst in public_instances:
            print(f"  • {inst['Name']} ({inst['Instance ID']}) - {inst['Public IP']}")
            print(f"    Open to internet: {inst['Open Ports/Rules']}")
        print()

def main():
    """
    Main function
    """
    print("AWS EC2 Instance Enumeration with Open Ports Analysis")
    print("=" * 150)
    print()
    
    instances = get_ec2_instances_with_ports()
    
    if instances is not None:
        print_instances(instances)
        print_summary(instances)
        
        # Optionally save to file
        save_option = input("\nWould you like to save this to a CSV file? (y/n): ")
        if save_option.lower() == 'y':
            try:
                import csv
                filename = 'ec2_instances_with_ports.csv'
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    if instances:
                        fieldnames = instances[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(instances)
                
                print(f"✓ Data saved to {filename}")
            except Exception as e:
                print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    main()
