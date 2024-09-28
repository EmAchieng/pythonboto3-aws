"""
Set up infrastructure components including VPC, subnet, internet gateway,
security group, and an EC2 instance with Nginx
"""

import time
import vpc
import subnet
import internet_gateway
import security_group
import ec2_instance

def wait_for_resource(resource_check_function, resource_id, resource_name, poll_interval=5, timeout=300):
    """
    Polls the status of a resource until it's available or the timeout is reached.

    :param resource_check_function: Function to check the status of the resource.
    :param resource_id: ID of the resource to check.
    :param resource_name: Name of the resource (for logging purposes).
    :param poll_interval: Time (in seconds) to wait between checks.
    :param timeout: Maximum time (in seconds) to wait for the resource.
    """
    elapsed_time = 0
    while elapsed_time < timeout:
        if resource_check_function(resource_id):
            print(f"{resource_name} is now ready.")
            return True
        print(f"Waiting for {resource_name} to be ready...")
        time.sleep(poll_interval)
        elapsed_time += poll_interval

    raise TimeoutError(f"Timeout while waiting for {resource_name} to be ready.")

if __name__ == "__main__":
    # VPC
    vpc_id = vpc.create_vpc("10.0.0.0/16")
    wait_for_resource_to_be_ready(vpc.check_vpc_status, vpc_id, "VPC")

    #  Subnet
    public_subnet_id = subnet.create_subnet(vpc_id, "10.0.1.0/24", "eu-central-2a")
     wait_for_resource_to_be_ready(subnet.check_subnet_status, public_subnet_id, "Subnet")

    #  Internet Gateway
    igw_id = internet_gateway.create_internet_gateway(vpc_id)
    wait_for_resource_to_be_ready(internet_gateway.check_igw_status, igw_id, "Internet Gateway")

    # Security Group
    sg_id = security_group.create_security_group(vpc_id, "nginx-sg", "Security group for Nginx")
    security_group.authorize_ingress(sg_id, 80, "tcp", "0.0.0.0/0")
    wait_for_resource_to_be_ready(security_group.check_sg_status, sg_id, "Security Group")

    # Route Table and Associated with Subnet
    route_table_id = route_table.create_route_table(vpc_id)
    route_table.associate_route_table(route_table_id, public_subnet_id)
    wait_for_resource_to_be_ready(route_table.check_route_table_status, route_table_id, "Route Table")

    # EC2 Instance with Nginx
    ami_id = os.getenv("AMI_ID")
    instance_type = os.getenv("INSTANCE_TYPE")
    key_name = os.getenv("KEY_NAME")
    instance_id = ec2_instance.create_ec2_instance(ami_id, instance_type, key_name, public_subnet_id, sg_id)
    public_ip = ec2_instance.get_instance_public_ip(instance_id)
    wait_for_resource_to_be_ready(ec2_instance.check_instance_status, instance_id, "EC2 Instance")

    # Public IP of the Instance
    public_ip = ec2_instance.get_instance_public_ip(instance_id)
    print(f"EC2 Instance Public IP: {public_ip}")
    
    # Print
    print("Setup complete.")
    print(f"You can access Nginx at http://{public_ip}/")
    print("Hello World from Nginx")

    # Launch Configuration
    launch_configuration_name = "my-launch-config"
    auto_scaling_group.create_launch_configuration(
        launch_configuration_name,
        ami_id,
        instance_type,
        key_name
    )
    print("Launch Configuration created.")

    # Auto Scaling Group
    auto_scaling_group_name = "my-auto-scaling-group"
    vpc_zone_identifier = public_subnet_id
    auto_scaling_group.create_auto_scaling_group(
        auto_scaling_group_name,
        launch_configuration_name,
        min_size=1,
        max_size=3,
        vpc_zone_identifier=vpc_zone_identifier
    )
    print("Auto Scaling Group created.")
