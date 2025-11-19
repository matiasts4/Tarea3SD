# Dockerfile para Hadoop + Pig - Tarea 3
FROM ubuntu:20.04

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias básicas
RUN apt-get update && apt-get install -y \
    openjdk-8-jdk \
    wget \
    ssh \
    rsync \
    python3 \
    python3-pip \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Configurar Java
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Descargar e instalar Hadoop 3.3.6
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

RUN wget -q https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} ${HADOOP_HOME} && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# Descargar e instalar Apache Pig 0.17.0
ENV PIG_VERSION=0.17.0
ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:$PIG_HOME/bin

RUN wget -q https://archive.apache.org/dist/pig/pig-${PIG_VERSION}/pig-${PIG_VERSION}.tar.gz && \
    tar -xzf pig-${PIG_VERSION}.tar.gz && \
    mv pig-${PIG_VERSION} ${PIG_HOME} && \
    rm pig-${PIG_VERSION}.tar.gz

# Configurar SSH para Hadoop (necesario para modo pseudo-distribuido)
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys

# Crear directorios para HDFS
RUN mkdir -p /opt/hadoop/hdfs/namenode && \
    mkdir -p /opt/hadoop/hdfs/datanode

# Copiar archivos de configuración de Hadoop
COPY hadoop-config/core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY hadoop-config/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY hadoop-config/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
COPY hadoop-config/yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml

# Configurar variables de entorno en hadoop-env.sh
RUN echo "export JAVA_HOME=${JAVA_HOME}" >> $HADOOP_CONF_DIR/hadoop-env.sh && \
    echo "export HADOOP_HOME=${HADOOP_HOME}" >> $HADOOP_CONF_DIR/hadoop-env.sh

# Instalar dependencias Python para análisis
RUN pip3 install --no-cache-dir psycopg2-binary pandas matplotlib seaborn wordcloud numpy matplotlib-venn

# Crear directorios de trabajo
RUN mkdir -p /app/data /app/results /app/scripts

# Copiar scripts Pig y stopwords
COPY scripts/ /app/scripts/

# Script de inicialización y ejecución
COPY run_analysis.sh /app/run_analysis.sh
RUN chmod +x /app/run_analysis.sh

# Exponer puertos de Hadoop
# 9870: NameNode Web UI
# 8088: ResourceManager Web UI
# 9000: HDFS
EXPOSE 9870 8088 9000

WORKDIR /app

# Comando por defecto
CMD ["/app/run_analysis.sh"]
