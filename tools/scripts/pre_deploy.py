import json
import os
from boto3 import client


class DeployChalice:
    
    def set_root_path(self, root_path):
        root = os.path.abspath(root_path)
        self.root_path = root
        
    def set_stage(self, stage: str = "dev"):
        self.stage = stage
        
    def set_region(self, region: str = "us-east-1"):
        self.region = region
        
    def aws_secrets_manager(self):
        self.set_stage()
        
        if self.stage == "dev":
            return client(
                "secretsmanager", 
                region_name=self.region,
                endpoint_url="http://localhost:4566"
            )
        else:
            return client("secretsmanager")
        
    def pre_deploy(self):
        self.set_root_path(".")
        self.set_stage("dev")
        self.set_region()
        
        # busca o arquivo de configuração dentro de .chalice
        with open(f"{self.root_path}/.chalice/config.json", "r") as f:
            config = json.load(f)
            
        
        
        

if __name__ == '__main__':
    deploy = DeployChalice()
    deploy.pre_deploy()