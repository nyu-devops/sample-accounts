# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:sp24

# Set up the Python development environment
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN sudo python -m pip install --upgrade pip poetry && \
    sudo poetry config virtualenvs.create false && \
    sudo poetry install
