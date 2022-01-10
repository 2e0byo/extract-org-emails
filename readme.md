# Script to extract emails from org files I use

This script extracts all emails from an 'email' column in a table in an org mode
file under a heading 'students'.

I organise my teaching with a heading per module, subheadings per group, and a
heading within `students` which contains a table with names, emails, columns for
attendance, etc.  This script dumps the emails into a single line pre-formatted
with `Bcc: ` to make emailing groups easy.

The script must be given a module and file.  If a subheading is given, the
*first* subheading which matches *under* the module heading will be returned.

Whilst likely useless for anyone else, it was a breeze to write and will be a
breeze to rewrite.
