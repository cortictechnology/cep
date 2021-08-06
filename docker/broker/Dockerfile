FROM erlang:22
RUN git clone https://github.com/emqx/emqx-rel.git 
WORKDIR emqx-rel
RUN make

FROM erlang:slim
RUN apt update
RUN apt -y install nano python3
WORKDIR /root/
COPY --from=0 /emqx-rel/_build/emqx/rel .
