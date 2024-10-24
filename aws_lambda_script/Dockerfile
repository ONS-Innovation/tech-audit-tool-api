# Use an official Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.10

# Set the working directory in the container
WORKDIR /var/task

# Copy the requirements.txt first to leverage Docker's cache for dependencies
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app folder (with your Flask app) and the lambda_handler.py
COPY app/ /var/task/app/
COPY main.py /var/task/

# The CMD specifies the handler to use in AWS Lambda
CMD ["main.lambda_handler"]
