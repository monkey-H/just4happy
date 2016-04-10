FROM ubuntu:14.04
MAINTAINER <nap 5681713@qq.com>

# todo: 基础镜像用到了rsyslog，使用ubuntu是否必要？

RUN apt-get update
RUN sed -i "s/#$ModLoad imudp/$ModLoad imudp/g" "/etc/rsyslog.conf"
RUN sed -i "s/#$UDPServerRun 514/$UDPServerRun 514/g" "/etc/rsyslog.conf"
RUN sed -i "s/#$ModLoad imtcp/$ModLoad imtcp/g" "/etc/rsyslog.conf"
RUN sed -i "s/#$InputTCPServerRun 514/$InputTCPServerRun 514/g" "/etc/rsyslog.conf"


