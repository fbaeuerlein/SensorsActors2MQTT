# Setup control and monitoring stack with docker-compose

This is the description to run a control and monitoring stack with docker. Inspired by https://github.com/ttncat/ttncat-docker-compose.

Following components are used:

- Mosquitto MQTT broker for sending/receiving messages
- Nodered for easy generation of data flows between the components
- Grafana for visualization of time series data
- InfluxDB for easy storage of time series data 

## Requirements

- mustache
- docker

## Create deployment settings automatically

### Configuration file for deployment

Modify the config_sample.json for password and user settings for the services.
Grafana is configured to automatically use the Influx service as a data source.
The sample config should be self explaining. 

The container name on influx determines the network-name of the service. This is needed for the grafana configuration.

Currently, for nodered, the credentials have to be entered manually if you want to push data to the Influx database.

### Run `deploy.sh` and deploy the services

Run `deploy.sh` within this folder with the modified configuration JSON file. A subfolder 'deployment' will be created, that contains the resulting docker-compose.yml and the required resources for docker-compose. So go folder deployment and run `docker-compse up (--build)` to start the services.

### Details of `deploy.sh`

See deploy.sh with comments

#### Nodered Authentication

Tutorial from https://nodered.org/docs/user-guide/runtime/securing-node-red#http-node-security

Create a bcrypt hashed password and adapt the settings.js accordingly.

To generate a hashed password, go to the nodered container with 

`docker exec -it container_id /bin/bash` 

and execute 

`node -e "console.log(require('bcryptjs').hashSync(process.argv[1], 8));" your-password-here`. 

### MQTT to Influx flow

See nodered folder in / and the sample_influx.json

### Enable docker-compose as system service

See https://gist.github.com/mosquito/b23e1c1e5723a7fd9e6568e5cf91180f