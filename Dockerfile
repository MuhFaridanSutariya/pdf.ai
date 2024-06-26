# Use an official Python runtime as a parent image
FROM python:3.8-slim

RUN useradd -m -u 1000 user
USER user

# Set the working directory in the container
WORKDIR /code

# Copy the current directory contents into the container at /app
COPY . /code

# RUN chown -R user:user /code

# Install any needed dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Command to run the app
CMD python -m chainlit run app.py -h --host 0.0.0.0