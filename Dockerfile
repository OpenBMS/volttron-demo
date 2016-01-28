FROM openbms/volttron:latest

ADD . /home/volttron/demo
RUN chown -R volttron:volttron /home/volttron/demo

ADD launch.sh /home/volttron/launch.sh
RUN chown -R volttron:volttron /home/volttron/launch.sh
RUN chmod +x /home/volttron/launch.sh

USER volttron

# Packages and installs dummy package
# Uses bash because non-interactive sh does not load startup files
RUN bash -c "volttron-pkg package ~/demo/entities/Test"
RUN bash -c "volttron-pkg configure ~/.volttron/packaged/testagent-0.1-py2-none-any.whl ~/demo/entities/Test/testagent.config"
RUN bash -c "volttron-ctl install ~/.volttron/packaged/testagent-0.1-py2-none-any.whl"

CMD ["bash"]
