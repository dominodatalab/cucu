FROM selenium/standalone-chrome:latest

############################################################
#
# VNC Settiings
#
############################################################
# Disable VNC password
ENV VNC_NO_PASSWORD=true
# Enlarge view area
ENV SE_SCREEN_WIDTH=1920
ENV SE_SCREEN_HEIGHT=1080

############################################################
#
# Core Requirements for Domino Data Lab environments
#
############################################################
#
# Allow build arguments to override defaults
ARG DUSER=ubuntu
ARG DGROUP=ubuntu
ARG ELANG=en_US.UTF-8
ARG PIP_PATH=/opt/conda/bin/pip
# use ARG to restrict noninteractive setting to build-time
ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.9.7

ENV DOMINO_USER=$DUSER
ENV DOMINO_GROUP=$DGROUP
ENV LANG=$ELANG
ENV R_VERSION=$R_VER
ENV PIP=$PIP_PATH
ENV SHELL=/bin/bash
ENV BASH_ENV=/etc/.bash_env

USER root

#
# Required: create a user and corresponding group account
#
RUN if ! id 12574 &> /dev/null; then \
        groupadd -g 12574 ${DOMINO_GROUP}; \
        useradd -u 12574 -g 12574 -m -N -s /bin/bash ${DOMINO_USER}; \
    fi && \
#
# Required: Set Domino workspace environment variables
#
# Must be set to a language supported by Domino to prevent unrecognized character input
    echo "export LANG=${LANG}" >> /home/${DOMINO_USER}/.domino-defaults && \
    echo "export LC_ALL=${LANG}" >> /home/${DOMINO_USER}/.domino-defaults && \
# Needed for proper filename handling in python
    echo 'export PYTHONIOENCODING=utf-8' >> /home/${DOMINO_USER}/.domino-defaults && \
# Prevent filling the working directory with jobs when using joblib for python
    echo 'export JOBLIB_TEMP_FOLDER=/tmp' >> /home/${DOMINO_USER}/.domino-defaults && \
    chown -R ${DOMINO_USER}.${DOMINO_GROUP} "/home/${DOMINO_USER}"
#
# Required: Install required OS packages for Domino
#
RUN apt-get update && apt-get install -y --no-install-recommends \
# The following packages are required
    apt-transport-https \
    apt-utils \
    gnupg2 \
    locales \
    software-properties-common \
    curl \
    git \
    openssh-server \
    rsync \
    sudo \
    vim \
    wget && \
# cleanup
    rm -rf /var/lib/apt/lists/* && \

# Recommended: Add domino user account to sudoers
#
    echo "${DOMINO_USER}    ALL=NOPASSWD: ALL" >> /etc/sudoers && \

#
# Recommended: Set appropriate locale
#
    locale-gen "${LANG}" && \
    update-locale LANG="${LANG}"

############################################################
#
# Python and packages and build environment
#
############################################################
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        wget \
        curl \
        llvm \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libxml2-dev \
        libxmlsec1-dev \
        libffi-dev \
        liblzma-dev && \
# cleanup
    rm -rf /var/lib/apt/lists/* && \
    rm -Rf /tmp/*

# Container should run as Ubuntu user
USER ubuntu
ENV HOME=/home/ubuntu

# Pyenv
RUN git clone https://github.com/pyenv/pyenv.git ${HOME}/.pyenv

ENV PYENV_ROOT=${HOME}/.pyenv
ENV PATH=${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}

RUN pyenv install ${PYTHON_VERSION} && \
    pyenv global ${PYTHON_VERSION} && \
    pyenv rehash

# Install python packages
ADD requirements.txt /
# TODO: Put reader creds in CI configuration
RUN pip install --extra-index-url \
    https://ddl-pypi-reader:pey_ASM7gu1muh@domino.jfrog.io/domino/api/pypi/pypi-private/simple cucu

ADD entry_point.sh /opt/bin/
ENTRYPOINT ["/opt/bin/entry_point.sh"]