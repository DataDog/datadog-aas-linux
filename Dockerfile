# Build process manager
FROM rust:latest as rust-binary
COPY /process_manager/ .
RUN rustup target add x86_64-unknown-linux-musl
RUN cargo build --release --target=x86_64-unknown-linux-musl

FROM ubuntu:latest as agent
# We extract the trace-agent from the agent and use a matching dogstatsd version
ARG AGENT_VERSION
ARG RELEASE_VERSION
# make the AGENT_VERSION arg mandatory
RUN : "${AGENT_VERSION:?AGENT_VERSION needs to be provided}"
RUN apt-get update
RUN apt-get install -y curl binutils zip
RUN mkdir ${RELEASE_VERSION}
COPY --from=rust-binary /target/x86_64-unknown-linux-musl/release/process_manager ${RELEASE_VERSION}/

# trace agent
RUN curl -LO https://apt.datadoghq.com/pool/d/da/datadog-agent_${AGENT_VERSION}-1_amd64.deb
RUN dpkg -i datadog-agent_${AGENT_VERSION}-1_amd64.deb
RUN mv opt/datadog-agent/embedded/bin/trace-agent ${RELEASE_VERSION}/

# dogstatsd
RUN curl -LO https://apt.datadoghq.com/pool/d/da/datadog-dogstatsd_${AGENT_VERSION}-1_amd64.deb
RUN dpkg -i datadog-dogstatsd_${AGENT_VERSION}-1_amd64.deb
RUN mv opt/datadog-dogstatsd/bin/dogstatsd ${RELEASE_VERSION}/

# strip binaries and zip folder for release
RUN strip /${RELEASE_VERSION}/*
RUN zip -r /datadog-aas-${RELEASE_VERSION}.zip /${RELEASE_VERSION}