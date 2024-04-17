import pulumi
import pulumi_aws as aws

config = pulumi.Config()

instance_type = config.get("instanceType")
vpc_network_cidr = config.get("vpcNetworkCidr")

ami = aws.ec2.get_ami(
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"],
        ),
    ],
    owners=["099720109477"],
    most_recent=True,
).id

vpc = aws.ec2.Vpc(
    "vpc",
    cidr_block=vpc_network_cidr,
    enable_dns_hostnames=True,
    enable_dns_support=True,
)

gateway = aws.ec2.InternetGateway("gateway", vpc_id=vpc.id)

subnet = aws.ec2.Subnet(
    "subnet", vpc_id=vpc.id, cidr_block="10.0.1.0/24", map_public_ip_on_launch=True
)

route_table = aws.ec2.RouteTable(
    "routeTable",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=gateway.id,
        )
    ],
)

route_table_association = aws.ec2.RouteTableAssociation(
    "routeTableAssociation", subnet_id=subnet.id, route_table_id=route_table.id
)

ports = (
    ("tcp", 80),
    ("tcp", 443),
    ("tcp", 22),
    ("tcp", 7777),
    ("tcp", 7778),
    ("tcp", 27015),
    ("udp", 7777),
    ("udp", 7778),
    ("udp", 27015),
)
ingress = [
    aws.ec2.SecurityGroupIngressArgs(
        from_port=port, to_port=port, protocol=protocol, cidr_blocks=["0.0.0.0/0"]
    )
    for protocol, port in ports
]

sec_group = aws.ec2.SecurityGroup(
    "secGroup",
    description="Enable HTTP access",
    vpc_id=vpc.id,
    ingress=ingress,
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

existing_key_pair = aws.ec2.KeyPair.get("existingKeyPair", "aws")

server = aws.ec2.Instance(
    "arkserver",
    instance_type=instance_type,
    subnet_id=subnet.id,
    vpc_security_group_ids=[sec_group.id],
    ami=ami,
    key_name=existing_key_pair.key_name,
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_size=30, volume_type="gp3"
    ),
    tags={
        "Name": "ark",
    },
)

pulumi.export("ip", server.public_ip)
pulumi.export("hostname", server.public_dns)
pulumi.export("url", server.public_dns.apply(lambda public_dns: f"http://{public_dns}"))
pulumi.export("user", server.user_data)
