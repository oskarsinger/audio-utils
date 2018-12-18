* Turn into Flask app with Celery stuff so I can repeatedly send new files to deal with. Maybe Dockerize. Why not?
* Develop better way to deal with artist metadata and avoid explicitly specifying directories and songs. Maybe can integrate with that terminal-based music manager? Maybe just deal with it in Postrgres DB.
* Parallelize where possible. Celery would actually take care of that.
* Figure out what happens if I try to write to a path that doesn't exist in Dropbox.
* Update everything to deal with DB instead of list files.
