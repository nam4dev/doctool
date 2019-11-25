{% if links %}
{% if title %}
.. _{{ title }}:

{{ title }}
{{ title_line }}
{% endif %}

.. toctree::
   :maxdepth: {{ maxdepth }}

   {% for link in links %}
   {{ link }}
   {% endfor %}
{% endif %}