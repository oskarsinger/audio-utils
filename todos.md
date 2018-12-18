* Turn into Flask app with Celery stuff so I can repeatedly send new files to deal with. Maybe Dockerize. Why not?
* Develop better way to deal with artist metadata and avoid explicitly specifying directories and songs. Maybe can integrate with that terminal-based music manager?
* Parallelize where possible. Celery would actually take care of that.
* Make more robust to errors.
	* Keep a file that tells which things were mid-download when things failed. I.e. write to the file before downloading, then delete the file only after download is complete. Probably database would be easier? Then I could add and delete entries concurrently with no concern for messing up file writing.
* Figure out what happens if I try to write to a path that doesn't exist in Dropbox.
