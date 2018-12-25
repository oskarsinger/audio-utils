* Turn into Flask app with Celery stuff so I can repeatedly send new files to deal with. Maybe Dockerize. Why not?
* Develop better way to deal with artist metadata and avoid explicitly specifying directories and songs. Maybe can integrate with Discogs API.
* Parallelize where possible. Celery would actually take care of a lot of that.
* Figure out what happens if I try to write to a path that doesn't exist in Dropbox.
* Consider using structlogs to do logging
* Should probably use Enum for some of the columns like "file_type"
* Set up explicit relations between AlbumRegistry, ArtistRegsistry, SongRegistry, etc. using `relationship` or `ForeignKey` or something like that.
* Speed up loading.
* Move most diagnostic prints to logging and use tqdm to show progress.
* Integrate all tools into one click file.
