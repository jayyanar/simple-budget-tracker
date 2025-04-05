# AWS SAM Template for Deploying Budget Tracker to Fargate

## Prompt

Generate AWS SAM template to deploy the containerized BudgetTracker Flask API to AWS Fargate. Ask me as input for VPC and Subnet Settings. Store the prompt under prompts and reasoning under the folder used for code creation as prompts/sam_fargate.md. Don't store the VPC information in md file.

## Implementation Reasoning

The AWS SAM template for deploying the Budget Tracker application to AWS Fargate was designed with the following considerations:

### 1. Infrastructure as Code Approach

The template uses AWS SAM (Serverless Application Model) and CloudFormation to define all required resources in a declarative manner, ensuring:
- Consistent deployments
- Version-controlled infrastructure
- Automated resource provisioning
- Easy updates and rollbacks

### 2. Container Deployment Strategy

The deployment strategy leverages:
- **Amazon ECR**: For storing the Docker container image
- **Amazon ECS with Fargate**: For running containers without managing servers
- **Application Load Balancer**: For distributing traffic and enabling high availability

This approach provides a scalable, managed container environment without the need to provision or manage EC2 instances.

### 3. Networking Configuration

The template configures networking with:
- **Existing VPC**: Using the provided VPC ID
- **Public Subnets**: Using the provided subnet IDs
- **Security Group**: Creating a new security group with appropriate ingress rules
- **Public IP Assignment**: Enabling public IP addresses for Fargate tasks

This configuration ensures the application is accessible from the internet while maintaining security.

### 4. Security Considerations

Security is addressed through:
- **IAM Roles**: Separate roles for task execution and task runtime with least privilege
- **Security Groups**: Restricting inbound traffic to necessary ports (5000 for the container, 80/443 for web traffic)
- **Private ECR Repository**: Securing container images
- **Logging**: Enabling CloudWatch logs for monitoring and troubleshooting

### 5. High Availability and Scalability

The template ensures reliability through:
- **Multiple Availability Zones**: Deploying across two subnets in different AZs
- **Load Balancing**: Distributing traffic across multiple container instances
- **Health Checks**: Monitoring container health and replacing unhealthy instances
- **Auto Scaling**: Configuring the service to scale between 1 and 5 tasks based on CPU utilization

### 6. Resource Optimization

Resources are optimized by:
- **Right-sizing Containers**: Configuring appropriate CPU and memory allocations
- **ECR Lifecycle Policies**: Automatically cleaning up old container images
- **Log Retention**: Setting appropriate retention periods for logs
- **Auto Scaling**: Running only the necessary number of containers based on demand

### 7. Deployment Workflow

The template facilitates a smooth deployment workflow:
1. Build the Docker image locally
2. Push the image to Amazon ECR
3. Deploy the SAM template to create/update the infrastructure
4. ECS automatically pulls the latest image and deploys it to Fargate

The outputs section provides helpful commands for the image push process.

## Auto Scaling Configuration

The template includes auto-scaling capabilities to optimize resource usage and cost:

1. **Minimum and Maximum Container Count**:
   - `MinContainerCount`: Set to 1 by default (reduced from 2 in the original template)
   - `MaxContainerCount`: Set to 5 by default

2. **CPU-Based Auto Scaling**:
   - Uses target tracking scaling based on CPU utilization
   - Target CPU utilization set to 70% by default
   - Scale-in cooldown: 300 seconds (5 minutes)
   - Scale-out cooldown: 60 seconds (1 minute)

3. **Auto Scaling Components**:
   - `AutoScalingRole`: IAM role with permissions for Application Auto Scaling
   - `ServiceScalingTarget`: Defines the scalable target (the ECS service)
   - `ServiceScalingPolicy`: Defines the scaling policy based on CPU utilization

This configuration ensures that:
- The service starts with just 1 container to minimize costs
- Additional containers are added automatically when CPU utilization exceeds 70%
- The service can scale up to 5 containers during high demand
- The service scales back down during periods of low demand

To modify these settings, you can adjust the following parameters:
- `MinContainerCount`: Minimum number of containers (default: 1)
- `MaxContainerCount`: Maximum number of containers (default: 5)
- `AutoScalingTargetCpuUtilization`: Target CPU utilization percentage (default: 70)

## Key Components

1. **ECR Repository**: Stores the Docker images with lifecycle policies
2. **ECS Cluster**: Manages the Fargate tasks
3. **Task Definition**: Defines the container configuration
4. **IAM Roles**: Provides necessary permissions
5. **Security Group**: Controls network access
6. **Load Balancer**: Distributes traffic and provides a stable endpoint
7. **ECS Service**: Maintains the desired number of tasks
8. **Auto Scaling**: Adjusts the number of tasks based on demand

## Troubleshooting

### Common Deployment Issues

1. **IAM Policy Error**: The original template used an incorrect policy ARN `AmazonECS-FullAccess` which doesn't exist. This was fixed by using the correct policy ARN `AmazonECS_FullAccess` (note the underscore instead of hyphen).

2. **Container Execution Error**: The original container configuration used Gunicorn which caused an "exec format error". This was fixed by:
   - Updating the container command to use Python directly: `Command: ["python", "src/app.py"]`
   - Ensuring the Flask app binds to all interfaces (0.0.0.0) in the app.py file

3. **Architecture Mismatch Error**: When deploying to Fargate, you might encounter "exec /usr/local/bin/python: exec format error" due to architecture incompatibility. This was fixed by:
   - Specifying the target platform in the Dockerfile: `FROM --platform=linux/amd64 python:3.11-slim`
   - This ensures the image is built for the x86_64/amd64 architecture used by AWS Fargate
   - This is particularly important when building on ARM-based machines like Apple M1/M2

4. **ECR Repository Already Exists**: When the ECR repository already exists, the deployment fails with an error: "Resource of type 'AWS::ECR::Repository' with identifier 'budget-tracker' already exists." This was fixed by:
   - Adding a parameter `CreateECRRepository` with default value "false"
   - Using a condition `ShouldCreateECRRepository` to control whether the repository is created
   - Setting the parameter to "true" only when you need to create a new repository

5. **VPC/Subnet Validation**: Ensure that the provided VPC and subnet IDs exist and are correctly formatted.

6. **Resource Naming Conflicts**: If you get naming conflicts during deployment, it might be because resources with the same names already exist. You can modify the resource names in the template or delete the existing resources.

## Usage Instructions

1. **Deploy the SAM template**:
   ```bash
   sam deploy --template-file template.yaml --stack-name budget-tracker --capabilities CAPABILITY_IAM
   ```

2. **Build and push the Docker image** (use the commands from the stack outputs):
   ```bash
   # Login to ECR
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   
   # Build the Docker image
   docker build -t budget-tracker:latest .
   
   # Tag the image
   docker tag budget-tracker:latest <account-id>.dkr.ecr.<region>.amazonaws.com/budget-tracker:latest
   
   # Push the image to ECR
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/budget-tracker:latest
   ```

3. **Access the application** using the LoadBalancer DNS name from the stack outputs

## Future Enhancements

1. **HTTPS Support**: Add an SSL/TLS certificate and configure HTTPS listeners
2. **More Advanced Auto Scaling**: Implement request count-based scaling in addition to CPU-based scaling
3. **CI/CD Pipeline**: Integrate with AWS CodePipeline for automated deployments
4. **Monitoring**: Add CloudWatch alarms and dashboards
5. **Database Integration**: Add RDS or DynamoDB for persistent storage
6. **Custom Domain**: Configure Route 53 for a custom domain name
7. **Cost Optimization**: Implement Fargate Spot for non-critical workloads
