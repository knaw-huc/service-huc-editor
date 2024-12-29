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

## Default credentials:

- admin API key: ``foobar``
- ``htp.test``: user ``test`` with password ``test``

**ALWAYS** change these when running a CCF production deployment!

- [admin API key](#access-to-the-admin-api)
- [user access](#access)

## Setup your own

### Create or select a CMDI profile

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

### Start the service

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

### Initialize your app

```sh
curl -v -X PUT -H 'Authorization: Bearer foobar' http://0.0.0.0:1210/app/myApp?prof=clarin.eu:cr1:p_1721373444008&desrc="my Application"
```

### Tweak the profile

To add cues to the profile you can download a template tweak file for your profile:

[http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak/template](http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak/template)

This template replicates the full structure of the profile, but this is not needed: only the path to the components or the elements that are tweaked are needed.

```xml
<ComponentSpec xmlns:clariah="http://www.clariah.eu/" xmlns:cue="http://www.clarin.eu/cmd/cues/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" isProfile="true" CMDVersion="1.2" CMDOriginalVersion="1.2" xsi:noNamespaceSchemaLocation="https://infra.clarin.eu/CMDI/1.x/xsd/cmd-component.xsd">
    <Header>
        <ID>clarin.eu:cr1:p_1721373444008</ID>
        <Name>ShowcaseForm</Name>
        <Description>A showcase profile for the CLARIAH CMDI Forms</Description>
        <Status>development</Status>
    </Header>
    <Component name="ShowcaseForm">
        <Element name="Hello">
            <clariah:label xml:lang="fr">Bonjour</clariah:label>
            <clariah:label xml:lang="nl">Hallo</clariah:label>            
        </Element>
    </Component>
</ComponentSpec>        
```

To update the tweaks use:
- \[``POST``\] to, e.g., http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak add a new tweak file, which will redirect you to the tweakfile created, e.g., http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008/tweak/1
- \[``PUT``\] to a specific tweak file to update it 
- \[``DELETE``\] a specific tweak file

Multiple tweak files can exist and will be applied in order. The (future) purpose is to have dedicated tweak files for labels in specific languages, or a tweak file for indexing details. The result can be seen by requesting the profile, e.g., http://localhost:1210/app/helloWorld/profile/clarin.eu:cr1:p_1721373444008

Here some example tweak files can be found:

- [clariah vocabulary](https://github.com/CLARIAH/vocab-registry-editor/blob/main/data/apps/vocabs/profiles/clarin.eu%3Acr1%3Ap_1653377925723/tweaks/tweak-1.xml)
- [hi data envelopes](https://github.com/knaw-huc/hi-data-envelop-editor/blob/main/data/apps/data-envelopes/profiles/clarin.eu%3Acr1%3Ap_1708423613607/tweaks/tweak-1.xml)
- [hi nde](https://github.com/knaw-huc/hi-nde-editor/blob/main/data/apps/nde/profiles/clarin.eu%3Acr1%3Ap_1708423613599/tweaks/tweak-1.xml)
- [iisg adoptie](https://code.huc.knaw.nl/tsd/sd-service-huc-editor/-/blob/main/data/apps/adoptie/profiles/clarin.eu:cr1:p_1721373443933/tweaks/tweak-1.xml?ref_type=heads) (HuC only)
- [iisg afstand](https://code.huc.knaw.nl/tsd/sd-service-huc-editor/-/blob/main/data/apps/afstand/profiles/clarin.eu:cr1:p_1721373443948/tweaks/tweak-1.xml?ref_type=heads) (HuC only)
- [niod yugo dre](https://github.com/knaw-huc/niod-dre-yugo-editor/blob/main/data/apps/yugo/profiles/clarin.eu%3Acr1%3Ap_1721373443934/tweaks/tweak-1.xml)

The next sections list the cues you can add to elements and components. 

#### CMDI cues

Since CMDI 1.2 cues for tools can be specified. CCF supports the following cues using this mechanism:

- ``cue:displayOrder``: change the order of the elements or components; this allows to mix them in the editor, which can't be done in the profile specification
- ``cue:inputWidth``: change how many characters width an input box is;
- ``cue:inputHeight``: change how many lines an input box is;
- ``cue:readonly``: if set to ``true`` the value of this element can't be changed;
- ``cue:hide``: if set to ``true`` this element or component won't be shown in the editor.

Cues are attributes in the namespace ``http://www.clarin.eu/cmd/cues/1`` on the element or component tag, e.g.,

```xml
<Element name="begeleidendeInstantiesPersonen" xmlns:cue="http://www.clarin.eu/cmd/cues/1" cue:displayOrder="45" cue:inputWidth="80" cue:inputHeight="6">
```

#### CCF cues

##### Multilingual labels

CMDI cues being attributes don't work together with ``xml:lang`` language attributes. To resolve this CCF uses the ``label`` element in the ``http://www.clariah.eu/`` namespace for multilingual labels, e.g.,

```xml
<Element name="Hello" xmlns:clariah="http://www.clariah.eu/">
    <clariah:label xml:lang="fr">Bonjour</clariah:label>
    <clariah:label xml:lang="nl">Hallo</clariah:label>            
</Element>
```

##### Vocabularies

CCF doesn't support the CMDI external vocabularies syntax yet. Currently you can specify an ``autocompleteURL`` in the ``http://www.clariah.eu/`` namespace:

```xml
<Element name="researchActivity" cue:class="skosType" xmlns:clariah="http://www.clariah.eu/">
    <clariah:autoCompleteURI>/proxy/skosmos/sd/tadirah</clariah:autoCompleteURI>
</Element>
```

The URI follows the follow pattern:
- ``proxy``: use the CCF proxy
- the proxy recipe, e.g., [`skosmos`](./src/public.py#L32)
- a specific instance of the recipe, e.g., [``sd``]./resources/proxies/skosmos-sd.toml) (see [](./resources/proxies/) for an overview)
- a vocab in that instance, e.g., ``tadirah``

#### CMDI auto values

CMDI 1.2 also added a way to specify auto values for an element, here the CCF supports:

- ``now`` for a date value scheme, will set the element to the current date

```xml
<Element name="modified">
    <AutoValue>now</AutoValue>
</Element>
```

#### Other tweaks

In the tweak file propererties of elements can be changed within limits:
- minimum and maximum cardinality within the original bounds
- vocabulary can be added as long as the values match the original value scheme

### Configure the app

Here are some example configurations:

- [clariah vocabulary](https://github.com/CLARIAH/vocab-registry-editor/blob/main/data/apps/vocabs/config.toml)
- [hi data envelopes](https://github.com/knaw-huc/hi-data-envelop-editor/blob/main/data/apps/data-envelopes/config.toml)
- [hi nde](https://github.com/knaw-huc/hi-nde-editor/blob/main/data/apps/nde/config.toml)
- [iisg adoptie](https://code.huc.knaw.nl/tsd/sd-service-huc-editor/-/blob/main/data/apps/adoptie/config.toml?ref_type=heads) (HuC only)
- [iisg afstand](https://code.huc.knaw.nl/tsd/sd-service-huc-editor/-/blob/main/data/apps/afstand/config.toml?ref_type=heads) (HuC only)
- [niod yugo dre](https://github.com/knaw-huc/niod-dre-yugo-editor/blob/main/data/apps/yugo/config.toml)

#### The columns in the record list

#### The record title

#### Styling

#### Access

#### Hooks

### configure the services

#### Access to the admin API

