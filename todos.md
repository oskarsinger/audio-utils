* Develop better way to deal with artist metadata and avoid explicitly specifying directories and songs. Maybe can integrate with Discogs API.
* Parallelize where possible. Celery would actually take care of a lot of that.
* Figure out what happens if I try to write to a path that doesn't exist in Dropbox.
* Should probably use Enum for some of the columns like "file_type"
* Set up explicit relations between AlbumRegistry, ArtistRegsistry, SongRegistry, etc. using `relationship` or `ForeignKey` or something like that.
* Integrate all tools into one click file.
* Figure out better way to deal with ID3 tags, either by changing database or translating in code.
* Consider schemaless for music metadata.
