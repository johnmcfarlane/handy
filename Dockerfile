FROM ubuntu:16.04

# for apt to be noninteractive
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

# fix bash, tmux, docker
RUN cp /etc/skel/.bashrc ~/ \
  && rm /etc/apt/apt.conf.d/docker-clean \
  && echo "set -g terminal-overrides 'xterm*:smcup@:rmcup@'" >> ~/.tmux.conf

# install system packages
RUN apt dist-upgrade --assume-yes
RUN apt-get update --quiet
RUN apt install --yes software-properties-common
RUN add-apt-repository --yes ppa:ubuntu-toolchain-r/test
RUN apt-get update --quiet
RUN apt-get install --quiet --yes bash-completion ccache clang-3.8 clang-3.9 clang-4.0 clang-5.0 clang-6.0 cmake gcc-5 g++-6 g++-7 g++-8 g++-9 git htop iputils-ping man nano tmux wget xz-utils
RUN apt-get install --quiet --yes python-pip
#RUN pip install conan

# get clang-7.1
RUN wget --quiet https://github.com/llvm/llvm-project/releases/download/llvmorg-7.1.0/clang+llvm-7.1.0-x86_64-linux-gnu-ubuntu-14.04.tar.xz \
  && tar xf clang+llvm-7.1.0-x86_64-linux-gnu-ubuntu-14.04.tar.xz

# install johnmcfarlane/bin
RUN cd ~ \
  && git clone https://github.com/johnmcfarlane/bin.git \
  && sed -i "s/#force_color_prompt=yes/force_color_prompt=yes/g" ~/.bashrc \
  && echo 'source "$HOME"/bin/on-terminal-start' >> ~/.bashrc

RUN update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-3.8 10 \
  && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-3.9 10 \
  && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-4.0 10 \
  && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-5.0 10 \
  && update-alternatives --install /usr/bin/clang++ clang++ /usr/bin/clang++-6.0 10 \
  && update-alternatives --install /usr/bin/clang++ clang++ /clang+llvm-7.1.0-x86_64-linux-gnu-ubuntu-14.04/bin/clang++ 10 \
  && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-5 10 \
  && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-6 10 \
  && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 10 \
  && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 10 \
  && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 10 \
  && update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++ 10 \
  && update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++ 10

RUN apt-get install --reinstall bash-completion
RUN apt-get install --quiet --yes cloc

CMD bash
