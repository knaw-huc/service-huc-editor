# CLARIAH CMDI Forms: services
*CCF backend services*

## demo: run the Hello World Form

1. Start the docker container:

```sh
docker build -t ccf .
docker run -p 1210:1210 --name=ccf --rm -it ccf
```

2. Initialize the HelloWorld app:

```sh
curl -v -X PUT -H 'Authorization: Bearer foobar' http://0.0.0.0:1210/app/HelloWorld
```

3. Visit the HelloWorld app:

[http://localhost:1210/app/HelloWorld](http://localhost:1210/app/HelloWorld)

## Setup your own

### create or select a CMDI profile

Create or select a [CMDI](http://www.clarin.eu/cmdi/) profile in/from the [Component Registry](https://catalog.clarin.eu/ds/ComponentRegistry/)

_CCF limitations_
* don't use attributes, as they are tied to XML and don't have a decent counterpart in JSON, RDF, ...

Remember the ID of your profile, which can be seen in its XML representation, e.g. `clarin.eu:cr1:p_1721373444008`:

```xml
<ComponentSpec isProfile="true" CMDVersion="1.2" CMDOriginalVersion="1.2">
  <Header>
    <ID>clarin.eu:cr1:p_1721373444008</ID>
    <Name>ShowcaseForm</Name>
    <Description>A showcase profile for the CLARIAH CMDI Forms</Description>
    <Status>development</Status>
  </Header>
```

### start the service

```sh
docker build -t ccf .
docker run -v ./conf:/home/huc/huc-editor-service/conf -v ./data:/home/huc/huc-editor-service/data -p 1210:1210 --name=ccf --rm -it ccf
```

This mounts both the local
- conf directory, containing the global configuration
- data directory, which will contain the app configuration, the profile, its tweak(s) and records

### initialize your app

```sh
curl -v -X PUT -H 'Authorization: Bearer foobar' http://0.0.0.0:1210/app/myApp?prof=clarin.eu:cr1:p_1721373444008&desrc="my Application"
```

### tweak the profile

To add cues to the profile you can download a template tweak file for your profile:

[http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak/template](http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak/template)

The next sections list the cues you can add there. Also see the various apps in the [data](data) directory. You'll find the tweak files under the profiles, e.g. [data/apps/data-envelopes/profiles/clarin.eu:cr1:p_1708423613607/tweaks/tweak-1.xml](data/apps/data-envelopes/profiles/clarin.eu:cr1:p_1708423613607/tweaks/tweak-1.xml).

#### CMDI cues

#### CLARIAH cues

### configure the app

## configure the services
