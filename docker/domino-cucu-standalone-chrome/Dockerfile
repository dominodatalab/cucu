FROM selenium/standalone-chrome:latest

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

ENV DOMINO_USER=$DUSER
ENV DOMINO_GROUP=$DGROUP
ENV LANG=$ELANG
ENV R_VERSION=$R_VER
ENV PIP=$PIP_PATH
ENV SHELL=/bin/bash

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
# Fix for sudo bug in 20.04 >>>is this valid?<<<
#    echo "Set disable_coredump false" >> /etc/sudo.conf && \
#
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
# Python
#
############################################################
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip && \
# cleanup
    rm -rf /var/lib/apt/lists/* && \
    rm -Rf /tmp/* && \
# Default to python3 (Ubuntu only)
    if [ -x /usr/bin/python3 ]; then \
        ln -sf /usr/bin/python3 /usr/bin/python; \
    fi && if [ -x /usr/bin/pip3 ]; then \
        ln -sf /usr/bin/pip3 /usr/bin/pip; \
    fi

# Container should run as user
USER ubuntu
ADD entrypoint.sh /opt/bin/
ENTRYPOINT ["/opt/bin/entry_point.sh"]