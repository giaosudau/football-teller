# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libffi-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Scrapy
RUN pip install scrapy==2.10.0 sqlalchemy==2.0.19 pymysql==1.1.0

# Copy project files
COPY . .


# Set entrypoint
ENTRYPOINT ["scrapy", "crawl"]