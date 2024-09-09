from diagrams import Diagram, Cluster
from diagrams.aws.compute import EKS
from diagrams.aws.network import VPC, PrivateSubnet, InternetGateway
from diagrams.aws.security import IAM
from diagrams.aws.storage import EBS
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Service

with Diagram("EKS Terraform Configuration", show=False):
    with Cluster("AWS Account"):
        vpc = VPC("VPC")
        
        with Cluster("EKS Cluster"):
            eks = EKS("EKS")
            
            with Cluster("Node Group"):
                workers = [Pod("Worker") for _ in range(3)]
            
            addons = [
                Service("CoreDNS"),
                Service("kube-proxy"),
                Service("vpc-cni"),
                Service("ebs-csi-driver"),
                Service("pod-identity-agent"),
                Service("s3-csi-driver")
            ]
        
        subnets = [PrivateSubnet("Subnet 1a"), PrivateSubnet("Subnet 1d")]
        igw = InternetGateway("Internet Gateway")
        
        iam = IAM("IAM Roles")
        ebs = EBS("EBS")
        
    vpc >> subnets
    vpc >> igw
    subnets >> eks
    eks >> workers[0]
    for worker in workers:
        worker >> addons
    iam >> eks
    ebs >> workers[0]

print("Diagram generated successfully.")
