# CLARIAH CMDI Forms: services
*CCF backend services*

## demo: run the Hello World Form

1. Start the docker container:

```sh
docker run -p 1210:1210 --name=ccf --rm -it ghcr.io/knaw-huc/service-huc-editor:2.0-RC1
```

2. Initialize the HelloWorld app:

```sh
curl -v -X PUT -H 'Authorization: Bearer foobar' http://localhost:1210/app/HelloWorld
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
  ...
</ComponentSpec>
```

### start the service

With release image:
```sh
docker run -v ./conf:/home/huc/huc-editor-service/conf -v ./data:/home/huc/huc-editor-service/data -p 1210:1210 --name=ccf --rm -it ghcr.io/knaw-huc/service-huc-editor:2.0-RC2
```

With local image:
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

This template replicates the full structure of the profile, but this is not needed: only the path to the components or the elements that are tweaked are needed.

- ``POST`` to http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak add a new tweak file, which will redirect you to the tweakfile created, e.g., http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak/1
- ``PUT`` to a specific tweak file to update it 
- ``DELETE`` a specific tweak file

Multiple tweak files can exist and will be applied in order. The (future) purpose is to have dedicated tweak files for labels in specific languages, or a tweak file for indexing details. The result can be seen by requesting the profile, e.g., http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008

Here are some example tweak files:

- [clariah vocabulary](https://github.com/CLARIAH/vocab-registry-editor/blob/main/data/apps/vocabs/profiles/clarin.eu%3Acr1%3Ap_1653377925723/tweaks/tweak-1.xml)
- [hi data envelopes](https://github.com/knaw-huc/hi-data-envelop-editor/blob/main/data/apps/data-envelopes/profiles/clarin.eu%3Acr1%3Ap_1708423613607/tweaks/tweak-1.xml)
- [hi nde](https://github.com/knaw-huc/hi-nde-editor/blob/main/data/apps/nde/profiles/clarin.eu%3Acr1%3Ap_1708423613599/tweaks/tweak-1.xml)
- [niod yugo dre](https://github.com/knaw-huc/niod-dre-yugo-editor/blob/main/data/apps/yugo/profiles/clarin.eu%3Acr1%3Ap_1721373443934/tweaks/tweak-1.xml)

The next sections list the cues you can add to elements. 

#### CMDI cues

Since CMDI 1.2 cues for tools can be specified. CCF supports the following using this mechanism:

- ``cue:displayOrder``
- ``cue:inputWidth``
- ``cue:inputHeight``
- ``cue:readonly``
- ``cue:hide``

#### CLARIAH cues

- ``clariah:label``
- ``clariah:autoCompleteURI``

#### CMDI auto values

- ``now``

### configure the app

Here are some example configurations:

- [clariah vocabulary](https://github.com/CLARIAH/vocab-registry-editor/blob/main/data/apps/vocabs/config.toml)
- [hi data envelopes](https://github.com/knaw-huc/hi-data-envelop-editor/blob/main/data/apps/data-envelopes/config.toml)
- [hi nde](https://github.com/knaw-huc/hi-nde-editor/blob/main/data/apps/nde/config.toml)
- [niod yugo dre](https://github.com/knaw-huc/niod-dre-yugo-editor/blob/main/data/apps/yugo/config.toml)


## configure the services
