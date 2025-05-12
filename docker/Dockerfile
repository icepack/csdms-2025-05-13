FROM firedrakeproject/firedrake:2025.4.0.post0

RUN cd $PETSC_DIR && \
    $PETSC_DIR/$PETSC_ARCH/lib/petsc/conf/reconfigure-$PETSC_ARCH.py \
        --download-eigen \
        --download-metis \
        --download-parmetis \
        --download-mmg \
        --download-parmmg && \
    make PETSC_DIR=${PETSC_DIR} PETSC_ARCH=${PETSC_ARCH} all

RUN apt update && \
    apt install -yq \
        ffmpeg \
        libglu1-mesa-dev \
        libxrender-dev \
        libxcursor-dev \
        libxft-dev \
        libxinerama-dev

RUN python3 -m pip install ipykernel jupyter jupyterlab && \
    python3 -m ipykernel install --name=firedrake

RUN echo "Defaults lecture = never" >> /etc/sudoers.d/privacy && \
    echo "ALL            ALL = (ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    useradd --create-home --shell /bin/bash --password $(openssl passwd -1 password) icepack && \
    usermod --append --groups sudo icepack

USER icepack
WORKDIR /home/icepack

RUN python3 -m pip install git+https://github.com/mesh-adaptation/animate.git && \
    python3 -m pip install git+https://github.com/icepack/icepack2.git
