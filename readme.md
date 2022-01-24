# Script to perform management tasks for classes I teach.

## Extract emails

This function extracts all emails from an 'email' column in a table in an org mode
file under a heading 'students'.

I organise my teaching with a heading per module, subheadings per group, and a
heading within `students` which contains a table with names, emails, columns for
attendance, etc.  This script dumps the emails into a single line pre-formatted
with `Bcc: ` to make emailing groups easy.

The script must be given a module and file.  If a subheading is given, the
*first* subheading which matches *under* the module heading will be returned.

Whilst likely useless for anyone else, it was a breeze to write and will be a
breeze to rewrite.

## Find Slackers

This function finds all students who have missed two seminars without being
excused.  Additionally, it searches to see if they have emailed me in the last 2
weeks, in which case I probably forgot to mark them excused.
