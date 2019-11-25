# Doctool - Auto Documentation Aggregator

Doctool is written in python overlaying Sphinx to enable multiple Sphinx projects to be aggregated
into a single web application.

**Multiple versions can be easily handled as well by this tool.**

Doctool is able to automatically handle one's code source, in order to generate API documentation.

**Doctool is released under the MIT License**

## Getting Started

Assuming virtual environment is already created at **~/virtualenv/documentation**, type in a shell,

```bash
source ~/virtualenv/documentation/bin/activate

git clone https://github.com/nam4dev/doctool.git
cd doctool/doctool/doctool

python main.py --help
```

## Global doctool_settings.json file

The global doctool_settings.json describes global context to generate documentations

```json
{
    "DEBUG": 0,
    "THEME": "bootstrap",
    "OUTPUT": "./documentation",
    "WORKING_DIR": "~/my_project",
    "ORGANISATION": "<ORGANISATION>",
    "LOG_LEVEL": "INFO",
    "HOME_ICON": "ice-lolly",
    "PY_VERSION": "3.8",
    "JIRA_PROJECT_URI": "https://jira.com/browse/",
    "ISSUE_TRACKER_URI": "https://jira.com/secure/CreateIssue!default.jspa",
    "ISSUE_TRACKER_TEXT": "Report an Issue",
    "USE_GOOGLE_DOCSTRING": true,
    "HOST": "(127.0.0.1|localhost)",
    "TITLE": "My Super software",
    "MASTER_TITLE": "My Documentation",
    "SUFFIX": "rst",
    "MAXDEPTH": 3,
    "OVERRIDE": 1,
    "GRAPHVIZ": {
        "dot": "",
        "dot_args": [],
        "output_format": "png"
    },
    "PLANTUML": {
        "java": "",
        "jar": "",
        "epstopdf": "epstopdf",
        "output_format": "png",
        "latex_output_format": "png"
    },
    "PROJECTS_MAP": {
        "home_doc": "./doc/home_doc",
        "user_doc": "./doc/user_doc",
        "developer_doc": "./doc/developer_doc",
        "api_doc": "./program/src",
        "contacts_doc": "./doc/contacts_doc",
        "downloads_doc": "./doc/downloads_doc"
    }
}
```

| Property                     | Description                                                                         |
|------------------------------|-------------------------------------------------------------------------------------|
| DEBUG                        | Running mode (If DEBUG is set to  1, more logs will be output)                      |
| THEME                        | Generated documentation theme (Only bootstrap is supported for now)                 |
| OUTPUT                       | Output location path (relative or absolute)                                         |
| WORKING_DIR                  | Optional absolute path where documentation(s) lies (default to where this file lies)|
| ORGANISATION                 | The organisation, company or whatever make sense                                    |
| LOG_LEVEL                    | The logging level while running                                                     |
| HOME_ICON                    | The icon used for the top-left home section of the generated documentation          |
| PY_VERSION                   | Python version to link to intersphinx parameters (used for API Documentation only)  |
| JIRA_PROJECT_URI             | The JIRA project URI (useful when one wants to use the added jira Sphinx roles      |
| ISSUE_TRACKER_URI            | The ISSUE tracker URI (used in the `ISSUE_TRACKER_TEXT` button                      |
| USE_GOOGLE_DOCSTRING         | Whether Google docstring are used when auto-generating API project's documentation  |
| HOST                         | Where the documentation is intended to be hosted (localhost, www.example.com)       |
| TITLE                        | The HTML title markup of the whole Documentation generated bundle                   |
| MASTER_TITLE                 | The title of the whole Documentation generated bundle                               |
| SUFFIX                       | Suffix used for the documentation (default to .rst)                                 |
| MAXDEPTH                     | The maximum depth of the generated toc tree(s) (HTML left & right menu)             |
| OVERRIDE                     | Whether previous generated documentation shall be override or not                   |
| GRAPHVIZ                     | GRAPHVIZ configuration                                                              |
| GRAPHVIZ.dot                 | GRAPHVIZ dot binary path                                                            |
| GRAPHVIZ.dot_args            | GRAPHVIZ arguments to be passed to the binary                                       |
| GRAPHVIZ.output_format       | GRAPHVIZ output format (default to png)                                             |
| PLANTUML                     | PLANTUML configuration                                                              |
| PLANTUML.java                | JAVA binary path                                                                    |
| PLANTUML.jar                 | PLANTUML JAVA jar path                                                              |
| PLANTUML.epstopdf            | default to epstopdf                                                                 |
| PLANTUML.output_format       | PLANTUML output format (default to png)                                             |
| PLANTUML.latex_output_format | PLANTUML latex output format (default to png)                                       |
| PROJECTS_MAP                 | A mapping hash table of documentation's id as key and its path as value             | 

## Per project doctool_settings.json file

For example in the directory ./doc/user_doc add a file named doctool_settings.json with following specification:

```json
{
    "name": "User Guide",
    "id": "user_doc",
    "rank": 1,
    "api": 0,
    "icon": "glyphicon glyphicon-education",
    "metadata": {
        "authors": ["Core Team"],
        "copyright": "",
        "version": "1.0.0.0",
        "release": ""
    },
    "extra_sys_paths": [
        "./program/src"
    ]
}
```

| Property           | Description                                                                                            |
|--------------------|--------------------------------------------------------------------------------------------------------|
| name               | The documentation human name or title                                                                  |
| id                 | The documentation id (to be optionally referenced into the global configuration file)                  |
| rank               | The documentation rank according to others (impact navigation & menu display order)                    |
| api                | Whether the documentation is an API (a python source code to auto-generated into Sphinx documentation) |
| icon               | The bootstrap icon (will be display wherever the documentation name appears)                           |
| maxdepth           | Maximum depth recursion (toc tree)                                                                     |
| metadata           | Documentation meta data                                                                                |
| metadata.authors   | Documentation's author(s) (ie. Core Team)                                                              |
| metadata.copyright | Documentation's copyrights                                                                             |
| metadata.version   | Documentation's version                                                                                |
| metadata.release   | Documentation's release number                                                                         |
| excluded_modules   | Any python module to be excluded from API generation (`api` shall be set to 1)                         |
| extra_sys_paths    | Any path to be added to the PYTHON sys.path module                                                     |
| api_options        | Any API option (ie. `members`, `undoc-members`, `show-inheritance`, ...)                               |

## Doctool Command Line options

**Usage :**

* **-l --list-projects**: Use this option to get an exhaustive list of known projects from your Configuration file.

* **-s, --simple**: Use this option to provide either a key from your Configuration file
    or a directory path containing ReSt files.

* **-b, --build**: Use this option to provide either a combination of keys from your Configuration file
    or a combination of directories path containing ReSt files.
    
* **-v, --version**: Use this option to provide the version of documentation to be build (used for multi-version docmentation).

* **-o, --output**: Use this option to provide output directory path where your documentation is to be generated.

* **-c, --conf-file**: Use this option to provide the configuration file path.

* **-t, --title**: Use this option to provide the title to your whole generated documentation as a string.

* **-tn, --theme-name**: Use this option to provide the Theme name
    to your whole generated documentation as a string.

    Available Theme(s) :

        #. bootstrap

* **-i, --interactive**: Use this option to get interactive mode.

## Doctool Custom ReSt roles & directives

### Jira Issue Role

```rest
:jira_issue:`TICKET-ID`
```

This will produce a link which is the combination of the link provided in the global doctool_settings.json (JIRA_PROJECT_URI) & the ID provided
In our example, it would generate,

```html
<a href="https://jira.com/browse/TICKET-ID">JIRA Issue TICKET-ID</a>
```

### Jira Story Role

```rest
:jira_story:`TICKET-ID`
```

This will produce a link which is the combination of the link provided in the global doctool_settings.json (JIRA_PROJECT_URI) & the ID provided
In our example, it would generate,

```html
<a href="https://jira.com/browse/TICKET-ID">JIRA Story TICKET-ID</a>
```

### Releases Directive

Allow one to dynamically generate an HTML Download page based on dynamic input.

```rest
Directive to insert release markups into a table.
It handles whatever it is needed to be rendered

The releases directive takes as positional & required argument a file path to a JSON file
It could also be a valid HTTP uri producing expected JSON schema.

The expected JSON schema could be as needed, there's no constraints!

For example,

    .. code-block:: json

        {
            "program": "<program name>",
            "releases": [
                {
                    "version": "1.0.0.0",
                    "date": "01-01-2019",
                    "mac": "https://site.com/mac-release.run",
                    "linux": "https://site.com/linux-release.run",
                    "windows": "https://site.com/windows-release.exe"
                }
            ]
        }

An optional argument `:format:` indicates in which format the directive's content is written.

Supported formats:

    - html
    - rest (rst)
    - any format the `.. raw::` directive takes

Examples::

    HTML example

    .. releases:: ./release_list.json
        :format: html

        {% for release in release %}

            <h1>{{ release['name'] }}</h1>

            <table class="table">
                <thead>
                    <tr>
                        <td>Linux</td>
                        <td>Windows</td>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{{ release['linux'] }}</td>
                        <td>{{ release['windows'] }}</td>
                    </tr>
                </tbody>
            </table>

        {% endfor %}

    RST example

    Generating REST format will allow one to take advantage of REST parser.
    For example, any title will be included into the TOC (represented into the right menu of the document)

    .. releases:: https://wwww.site.com/release_list.json
        :format: rest

        {% macro raw_tag() %}
        .. raw:: html
        {% endmacro %}

        {% macro to_title(release) %}
        {%- set title=release['name'] -%}
        {{ title }}
        {{ '#' * title|length }}
        {% endmacro %}

        {% for release in release %}

        {{ to_title(release) }}
        {{ raw_tag() }}

            <table class="table">
                <thead>
                    <tr>
                        <td>Linux</td>
                        <td>Windows</td>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{{ release['linux'] }}</td>
                        <td>{{ release['windows'] }}</td>
                    </tr>
                </tbody>
            </table>

        {% endfor %}
```

## Structure Example

Assuming one gets a documentation folder in its home folder where its Home, User, Developer, Contacts & Downloads documentations are located.

- source_code
    - doctool_settings.json (**API project configuration file**)
- Documentation
    - home_doc
        - index.rst
        - doctool_settings.json
    - user_doc
        - doctool_settings.json
    - developer_doc
        - doctool_settings.json
    - contacts_doc
        - doctool_settings.json
    - downloads_doc
        - doctool_settings.json  (**Per project configuration file**)
    - doctool_settings.json  (**Global configuration file**)

## Documentation bundle generation

In order to generate one's bundle of documentation projects, type in a shell,

```bash
source ~/virtualenv/documentation/bin/activate
cd doctool/doctool/doctool

python main.py -v ${VERSION} -c "~/documentation/doctool_settings.json" -b developer_doc api_doc
```

Assuming one already create,
 - its virtual environment at **~/virtualenv/documentation**
 - its Documentation projects into **~/documentation**
 - its doctool_settings.json global configuration file referencing **developer_doc** & **api_doc** project's ID
 
 
 ## Contributing
 
 Anyone who values this project is welcomed to contribute.
 
 Following good practices are to be followed:
 
    - Add documentation whenever it could be
    - Add coverage
    
### Testing

```bash
git clone git+https://github.com/nam4dev/doctool.git

cd doctool
source ~/virtualenv/documentation/bin/activate
pip install -r requirements.txt

cd test
python runner.py
```
