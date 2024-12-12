FROM python:3.12
LABEL maintainer="mnie"

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY . /app

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install your package in editable mode
RUN pip3 install -e .

# Expose the port
EXPOSE 8000

# Use full path to the command if it's a CLI tool
CMD ["kids_box"]
