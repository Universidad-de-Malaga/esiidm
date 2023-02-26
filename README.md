# European Student Identifier Identity Management (ESIIdM)


--------------
# What's this code for

This code is a Dango application for managing basic student data that allows
Higher Education Institutions to use the MyAcademicId services that are part
of the European Student Card Infrastructure, using EduGAIN identity federation.

It can be used at any level, from a whole country down to a single institution.

--------------
# Installation

- Add 'esiidm' to the Django project installed apps in settings.
- Add the application to the project urls.py with

   ```python
   url(r'^esiidm/', include('esiidm.urls')),
   ```

- Finally, _makemigrations_ and _migrate_

--------------
# Usage

1. Create 
2. Go to your project "esiidm" URL with a browser.
3. Add

--------------
# Acknowledgements

This software has been partially developed with support of the CEF EDSSI project
Grant No. CEF-TC-2019-4-001.

The first deployment as a system for Spanish non-University Erasmus+ students
has been done under a collaboration agreement between SEPIE, RedIRIS/Red.es
and UMA.

This people have invested time and ideas for producing it:

- Victoriano Giralt (main coder, all bugs are mine).
- Fernando Bautista (main tester, translator)
- José Manuel Macias (verifier, translator)
- Francisco Aragó (verifier)
