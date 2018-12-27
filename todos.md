# Efficiency
* Parallelize where possible. Pathos or Celery?

# Dropbox
* Figure out what happens if I try to write to a path that doesn't exist in Dropbox.

# Database
* Should probably use Enum for some of the columns like "file_type"
* Set up explicit relations between AlbumRegistry, ArtistRegsistry, SongRegistry, etc. using `relationship` or `ForeignKey` or something like that.
* Consider schemaless for music metadata.
* Consider distributed database so the DB can be stored on my external drive.
* Include some functionality for updating a database from the local media dir, and call that in the database initialization tool.

# Usability
* Integrate all tools into one click file.
* Develop better way to deal with artist metadata (especially ID3 tag) and avoid explicitly specifying directories and songs. Maybe can integrate with Discogs API.

# Logging
* Keep tuning and improving the logging. Structlog is really powerful. Let's use its capabilities fully where it helps.
