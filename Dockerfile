FROM fedora:34

ARG UID=1000
ARG GID=365
ARG USERNAME
ARG GROUPNAME
ARG PROJECT_PATH

LABEL name="ALMA-DSpace Synchronizator" maintainer="Jakub Řihák, Central Library, Charles University, 2022"

RUN dnf update -y --refresh && dnf install -y --refresh \
        python3 \
        python3-devel \
        git \
        libtool \
        libevent-devel \
        iputils \
        net-tools \
        vim \
        wget

RUN dnf groupinstall --refresh -y \
    "Development Tools" \
    "Development Libraries"

RUN pip install --upgrade pip && pip install wheel

# Dockerfile expects to fined app code in './app' directory relative to its location
# clone oficial repo or your fork in to ./app folder first
COPY ./app /app

RUN groupadd --gid $GID $GROUPNAME \
    && useradd -r --uid ${UID} --gid $GID -m $USERNAME \
    && chown -R $UID:$GID /app \
    && chmod +x /app/entrypoint.sh

WORKDIR /app/

RUN pip install -r requirements.txt

ENTRYPOINT [ "/app/entrypoint.sh" ]