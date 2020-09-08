FROM golang:1.12.6 AS tfmask

RUN git clone https://github.com/cloudposse/tfmask.git
RUN cd tfmask && make && make go/build

FROM debian:buster-slim as base

ARG DEFAULT_TF_VERSION=0.13.1
ARG TFSWITCH_VERSION=0.8.832

# Terraform environment variables
ENV CHECKPOINT_DISABLE=true
ENV TF_IN_AUTOMATION=yep
ENV TF_INPUT=false
ENV TF_PLUGIN_CACHE_DIR=/usr/local/share/terraform/plugin-cache

RUN apt-get update && apt-get install -y \
    git \
    ssh \
    tar \
    gzip \
    ca-certificates \
    curl \
    unzip \
    jq \
    python2 \
    python3 \
    python3-requests \
    python3-pip \
    wget \
 && rm -rf /var/lib/apt/lists/*

RUN curl -fsL https://github.com/warrensbox/terraform-switcher/releases/download/${TFSWITCH_VERSION}/terraform-switcher_${TFSWITCH_VERSION}_linux_amd64.tar.gz -o tfswitch.tar.gz \
 && tar -xvf tfswitch.tar.gz \
 && mv tfswitch /usr/local/bin \
 && rm -rf tfswitch \
 && tfswitch $DEFAULT_TF_VERSION
RUN mkdir -p $TF_PLUGIN_CACHE_DIR

COPY --from=tfmask /go/tfmask/release/tfmask /usr/local/bin/tfmask
ENV TFMASK_RESOURCES_REGEX="(?i)^(random_id|kubernetes_secret|acme_certificate).*$"

COPY entrypoints/ /entrypoints/
COPY actions.sh /usr/local/actions.sh

COPY tools/convert_validate_report.py /usr/local/bin/convert_validate_report
COPY tools/github_pr_comment.py /usr/local/bin/github_pr_comment
COPY tools/latest_terraform_version.py /usr/local/bin/latest_terraform_version
COPY tools/convert_output.py /usr/local/bin/convert_output
COPY tools/plan_cmp.py /usr/local/bin/plan_cmp
COPY tools/convert_version.py /usr/local/bin/convert_version
COPY tools/workspace_exists.py /usr/local/bin/workspace_exists

ENTRYPOINT ["/usr/local/bin/terraform"]
